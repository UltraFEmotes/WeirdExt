// WeirdExt overlay helper: Dear ImGui on Metal, driven by JSON lines on stdin.
// Python owns all memory access. This process draws, relays input state and
// posts bounded mouse deltas; it never receives a task port.

#define IMGUI_DEFINE_MATH_OPERATORS
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#import <Carbon/Carbon.h>
#import <IOKit/hidsystem/IOLLEvent.h>
#import <ImageIO/ImageIO.h>
#import <Metal/Metal.h>
#import <MetalKit/MetalKit.h>

#include <algorithm>
#include <cfloat>
#include <cmath>
#include <iostream>
#include <map>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "imgui.h"
#include "imgui_impl_metal.h"
#include "imgui_impl_osx.h"

namespace {

constexpr double kTickHz = 60.0;
constexpr double kFrameMaxAge = 0.25;
constexpr double kAimMaxStep = 35.001;
constexpr double kAimMaxAge = 0.15;  // reads routinely take 40-80 ms; older than this is stale
constexpr double kWindowPollInterval = 0.25;
constexpr double kWindowLossGrace = 0.5;
constexpr double kToastLifetime = 4.0;
constexpr int kNameLimit = 40;
constexpr int kToastLimit = 44;
constexpr float kFontSize = 14.0f;
constexpr float kLabelSize = 13.0f;
struct Accent {
    const char* name;
    ImU32 color;
};

struct Base {
    const char* name;
    ImVec4 background, sidebar, card;
};

// One accent at a time colors the menu, ESP boxes and watermark.
const Accent kAccents[] = {{"Violet", IM_COL32(140, 120, 255, 255)}, {"Crimson", IM_COL32(235, 72, 90, 255)},
                           {"Ocean", IM_COL32(45, 165, 255, 255)}, {"Emerald", IM_COL32(40, 205, 140, 255)},
                           {"Amber", IM_COL32(255, 176, 46, 255)}, {"Rose", IM_COL32(255, 110, 180, 255)},
                           {"Mono", IM_COL32(225, 227, 235, 255)}};
const Base kBases[] = {
    {"Graphite", {0.055f, 0.059f, 0.071f, 1}, {0.040f, 0.043f, 0.053f, 1}, {0.075f, 0.080f, 0.096f, 1}},
    {"OLED", {0.012f, 0.012f, 0.016f, 1}, {0.000f, 0.000f, 0.000f, 1}, {0.036f, 0.037f, 0.044f, 1}},
    {"Slate", {0.075f, 0.090f, 0.120f, 1}, {0.058f, 0.070f, 0.096f, 1}, {0.098f, 0.115f, 0.150f, 1}}};
int accentIndex = 0, baseIndex = 0;
bool showWatermark = true;

// Hit sounds (overlay only; nothing is written to the game).
enum HitMode { HitOnDamage, HitOnShoot };
bool hitEnabled = false;
int hitMode = HitOnDamage;
int hitSound = 0;
double hitVolume = 70;
constexpr double kHitWindow = 0.35;  // seconds after a click in which an enemy health drop counts as your hit

ImU32 accentU32() { return kAccents[accentIndex].color; }
const Base& base() { return kBases[baseIndex]; }
constexpr ImU32 kShadow = IM_COL32(0, 0, 0, 200);
constexpr const char* kFontPath = "/System/Library/Fonts/SFNS.ttf";

double uptime() { return NSProcessInfo.processInfo.systemUptime; }

void emit(NSDictionary* event) {
    NSData* data = [NSJSONSerialization dataWithJSONObject:event options:0 error:nil];
    if (data == nil) return;
    NSMutableData* line = [data mutableCopy];
    [line appendBytes:"\n" length:1];
    [NSFileHandle.fileHandleWithStandardOutput writeData:line];
}

// ---- Packet decoding --------------------------------------------------------

std::optional<double> number(NSDictionary* dict, NSString* key) {
    id value = dict[key];
    if (![value isKindOfClass:NSNumber.class]) return std::nullopt;
    double result = [value doubleValue];
    return std::isfinite(result) ? std::optional<double>(result) : std::nullopt;
}

std::string text(NSDictionary* dict, NSString* key, int limit = 0) {
    id value = dict[key];
    if (![value isKindOfClass:NSString.class]) return {};
    NSString* string = value;
    if (limit > 0 && string.length > (NSUInteger)limit) {
        string = [string substringWithRange:[string rangeOfComposedCharacterSequencesForRange:NSMakeRange(0, limit)]];
    }
    return string.UTF8String ?: "";
}

bool flag(NSDictionary* dict, NSString* key) {
    id value = dict[key];
    return [value isKindOfClass:NSNumber.class] && [value boolValue];
}

NSDictionary* object(NSDictionary* dict, NSString* key) {
    id value = dict[key];
    return [value isKindOfClass:NSDictionary.class] ? value : nil;
}

struct Marker {
    double x = 0, y = 0, distance = 0;
    std::optional<double> w, h;
    std::string name;
    std::vector<float> bones;  // normalized x1, y1, x2, y2 per bone
    std::optional<double> health;  // 0..1
    int team = 0;
    std::optional<ImU32> color;  // the Team's real TeamColor
};

std::optional<ImU32> teamRgb(NSDictionary* entry) {
    NSArray* rgb = entry[@"color"];
    if (![rgb isKindOfClass:NSArray.class] || rgb.count != 3) return std::nullopt;
    return IM_COL32([rgb[0] intValue], [rgb[1] intValue], [rgb[2] intValue], 255);
}

struct PlayerRow {
    long long key = 0;
    std::string name;
    std::optional<double> health;  // 0..1
    double distance = 0;
    int team = 0;
    std::optional<ImU32> color;  // the Team's real TeamColor
    bool teammate = false;
};

struct Offscreen {
    double angle = 0, distance = 0;
    std::string name;
    int team = 0;
    std::optional<ImU32> color;  // the Team's real TeamColor
};

struct AimStep {
    double dx = 0, dy = 0;
    std::string name;
};

struct Toast {
    std::string text;
    double age = 0;
};

struct RenderOptions {
    bool enabled = true, boxes = true, names = true, distances = true, centerMarker = true;
    bool skeleton = false, tracers = false, offscreen = false, health = true;
};

struct SilentTarget {
    double x, y;
    std::string name;
};

struct DisplayFrame {
    int roster = 0;
    std::vector<PlayerRow> players;
    long long spectating = 0;
    std::string playerStatus;
    bool spectateAvailable = false, teleportAvailable = false;
    bool silentAvailable = false, silentEnabled = false;
    std::string silentStatus;
    std::optional<double> silentRadius;
    std::optional<SilentTarget> silentTarget;
    std::vector<Marker> targets;
    std::vector<Offscreen> offscreen;
    std::string status;
    bool complete = true;
    double readMs = 0;
    RenderOptions options;
    std::optional<std::pair<double, double>> boresight;
    bool movementAvailable = false, cameraAvailable = false, noclipAvailable = false;
    std::string movementStatus, cameraStatus, noclipStatus, aimMethod;
    bool aimEnabled = false;
    std::optional<double> aimRadius;
    std::optional<AimStep> aim;
    std::vector<Toast> toasts;
};

std::optional<DisplayFrame> decodeFrame(NSDictionary* packet) {
    NSArray* targets = packet[@"targets"];
    if (![targets isKindOfClass:NSArray.class] || ![packet[@"status"] isKindOfClass:NSString.class]) {
        return std::nullopt;
    }
    DisplayFrame frame;
    frame.status = text(packet, @"status");
    frame.roster = (int)number(packet, @"roster").value_or(0);
    if (NSArray* players = packet[@"players"]; [players isKindOfClass:NSArray.class]) {
        for (NSDictionary* entry in players) {
            if (![entry isKindOfClass:NSDictionary.class] || ![entry[@"key"] isKindOfClass:NSNumber.class]) {
                return std::nullopt;
            }
            frame.players.push_back({[entry[@"key"] longLongValue], text(entry, @"name", kNameLimit),
                                     number(entry, @"health"), number(entry, @"distance").value_or(0),
                                     (int)number(entry, @"team").value_or(0), teamRgb(entry), flag(entry, @"teammate")});
        }
    }
    if ([packet[@"spectating"] isKindOfClass:NSNumber.class]) frame.spectating = [packet[@"spectating"] longLongValue];
    frame.playerStatus = text(packet, @"player_status");
    frame.spectateAvailable = flag(packet, @"spectate_available");
    frame.teleportAvailable = flag(packet, @"teleport_available");
    frame.silentAvailable = flag(packet, @"silent_available");
    frame.silentStatus = text(packet, @"silent_status");
    frame.silentEnabled = flag(packet, @"silent_enabled");
    frame.silentRadius = number(packet, @"silent_radius");
    if (NSDictionary* target = object(packet, @"silent_target")) {
        auto x = number(target, @"x"), y = number(target, @"y");
        if (x && y) frame.silentTarget = SilentTarget{*x, *y, text(target, @"name")};
    }
    frame.complete = packet[@"complete"] == nil || flag(packet, @"complete");
    frame.readMs = std::max(0.0, number(packet, @"read_ms").value_or(0));
    for (NSDictionary* entry in targets) {
        if (![entry isKindOfClass:NSDictionary.class]) return std::nullopt;
        auto x = number(entry, @"x"), y = number(entry, @"y"), distance = number(entry, @"distance");
        if (!x || !y || !distance) return std::nullopt;
        Marker marker{*x, *y, *distance, number(entry, @"w"), number(entry, @"h"),
                      text(entry, @"name", kNameLimit), {}, number(entry, @"health"),
                      (int)number(entry, @"team").value_or(0), teamRgb(entry)};
        if (NSArray* bones = entry[@"bones"]; [bones isKindOfClass:NSArray.class] && bones.count % 4 == 0) {
            for (NSNumber* value in bones) {
                if (![value isKindOfClass:NSNumber.class] || !std::isfinite(value.doubleValue)) return std::nullopt;
                marker.bones.push_back(value.floatValue);
            }
        }
        frame.targets.push_back(std::move(marker));
    }
    if (NSArray* offscreen = packet[@"offscreen"]; [offscreen isKindOfClass:NSArray.class]) {
        for (NSDictionary* entry in offscreen) {
            if (![entry isKindOfClass:NSDictionary.class]) return std::nullopt;
            auto angle = number(entry, @"angle"), distance = number(entry, @"distance");
            if (!angle || !distance) return std::nullopt;
            frame.offscreen.push_back({*angle, *distance, text(entry, @"name", kNameLimit),
                                       (int)number(entry, @"team").value_or(0), teamRgb(entry)});
        }
    }
    if (NSDictionary* options = object(packet, @"options")) {
        frame.options = {flag(options, @"enabled"), flag(options, @"boxes"), flag(options, @"names"),
                         flag(options, @"distances"), flag(options, @"center_marker"), flag(options, @"skeleton"),
                         flag(options, @"tracers"), flag(options, @"offscreen"), flag(options, @"health")};
    }
    if (NSDictionary* bore = object(packet, @"boresight")) {
        auto bx = number(bore, @"x"), by = number(bore, @"y");
        if (bx && by) frame.boresight = std::make_pair(*bx, *by);
    }
    frame.movementAvailable = flag(packet, @"movement_available");
    frame.cameraAvailable = flag(packet, @"camera_available");
    frame.noclipAvailable = flag(packet, @"noclip_available");
    frame.movementStatus = text(packet, @"movement_status");
    frame.cameraStatus = text(packet, @"camera_status");
    frame.noclipStatus = text(packet, @"noclip_status");
    frame.aimMethod = text(packet, @"aim_method");
    frame.aimEnabled = flag(packet, @"aim_enabled");
    frame.aimRadius = number(packet, @"aim_radius");
    if (NSDictionary* aim = object(packet, @"aim")) {
        auto dx = number(aim, @"dx"), dy = number(aim, @"dy");
        if (dx && dy) frame.aim = AimStep{*dx, *dy, text(aim, @"name")};
    }
    if (NSArray* toasts = packet[@"toasts"]; [toasts isKindOfClass:NSArray.class]) {
        for (NSDictionary* toast in toasts) {
            if (![toast isKindOfClass:NSDictionary.class]) continue;
            if (auto age = number(toast, @"age")) frame.toasts.push_back({text(toast, @"text", kToastLimit), *age});
        }
    }
    return frame;
}

struct ExpNode {
    std::string name, cls;
    bool truncated = false;
    std::vector<ExpNode> kids;
    std::string address, parent;
};

ExpNode decodeNode(NSDictionary* dict) {
    ExpNode node{text(dict, @"name"), text(dict, @"cls"), flag(dict, @"truncated"), {},
                 text(dict, @"addr"), text(dict, @"parent")};
    if (node.cls.empty()) node.cls = "?";
    if (NSArray* kids = dict[@"kids"]; [kids isKindOfClass:NSArray.class]) {
        for (NSDictionary* kid in kids) {
            if ([kid isKindOfClass:NSDictionary.class]) node.kids.push_back(decodeNode(kid));
        }
    }
    return node;
}

bool containsCaseless(const std::string& haystack, const std::string& needle) {
    return [@(haystack.c_str()) localizedCaseInsensitiveContainsString:@(needle.c_str())];
}

std::vector<ExpNode> filterTree(const std::vector<ExpNode>& nodes, const std::string& query) {
    if (query.empty()) return nodes;
    std::vector<ExpNode> result;
    for (const ExpNode& node : nodes) {
        auto kids = filterTree(node.kids, query);
        if (containsCaseless(node.name, query) || containsCaseless(node.cls, query) || !kids.empty()) {
            result.push_back({node.name, node.cls, node.truncated, std::move(kids), node.address, node.parent});
        }
    }
    return result;
}

// ---- Settings mirror of rbxl/esp_settings.py ---------------------------------

struct Slider {
    const char* key;
    double low, high;
    bool integral;
};

const Slider kSliders[] = {
    {"box_height", 1, 20, false}, {"box_ratio", 0.2, 2, false}, {"fps", 1, 60, true},
    {"fov", 30, 120, true}, {"walk_speed", 0, 150, true}, {"jump_power", 0, 200, true},
    {"aim_radius", 20, 400, true}, {"aim_smoothing", 1, 20, true}, {"fly_speed", 5, 300, true}, {"aim_health_value", 1, 1000, true},
    {"silent_radius", 20, 600, true},
};

const std::map<std::string, std::vector<std::string>> kChoices{
    {"aim_method", {"mouse", "camera"}}, {"aim_part", {"head", "torso", "closest"}},
    {"aim_priority", {"crosshair", "distance"}}};

// Features that write game memory: never restored from disk, always start off.
const char* const kWriteFeatures[] = {"walk_speed_enabled", "jump_power_enabled", "noclip",
                                      "infinite_jump", "fov_enabled", "aim_enabled", "fly", "silent_aim"};

bool isWriteFeature(const std::string& key) {
    return std::any_of(std::begin(kWriteFeatures), std::end(kWriteFeatures),
                       [&](const char* feature) { return key == feature; });
}

struct Settings {
    std::map<std::string, bool> toggles{
        {"esp_enabled", true}, {"boxes", true}, {"names", true}, {"distances", true},
        {"center_marker", true}, {"show_local", false}, {"fov_enabled", false},
        {"walk_speed_enabled", false}, {"jump_power_enabled", false}, {"aim_enabled", false},
        {"noclip", false}, {"infinite_jump", false}, {"esp_skeleton", false}, {"esp_tracers", false},
        {"esp_offscreen", false}, {"esp_health", true}, {"team_check", false}, {"aim_sticky", true},
        {"fly", false}, {"aim_health_check", false}, {"silent_aim", false},
        {"silent_show_fov", true}};
    std::map<std::string, double> numbers{
        {"box_height", 5.4}, {"box_ratio", 0.6}, {"fps", 60}, {"fov", 70}, {"walk_speed", 16},
        {"jump_power", 50}, {"aim_radius", 140}, {"aim_smoothing", 6}, {"fly_speed", 50}, {"aim_health_value", 50},
        {"silent_radius", 160}};
    std::map<std::string, std::string> choices{
        {"aim_method", "mouse"}, {"aim_part", "torso"}, {"aim_priority", "crosshair"}};

    NSDictionary* snapshot(bool includeWrites = true) const {
        NSMutableDictionary* result = [NSMutableDictionary dictionary];
        for (const auto& [key, value] : toggles) {
            if (includeWrites || !isWriteFeature(key)) result[@(key.c_str())] = @(value);
        }
        for (const auto& [key, value] : numbers) result[@(key.c_str())] = @(value);
        for (const auto& [key, value] : choices) result[@(key.c_str())] = @(value.c_str());
        return result;
    }

    void apply(NSDictionary* incoming, bool includeWrites = true) {
        for (NSString* key in incoming) {
            std::string name = key.UTF8String;
            id value = incoming[key];
            if (choices.count(name) && [value isKindOfClass:NSString.class]) {
                const auto& allowed = kChoices.at(name);
                std::string choice = [value UTF8String];
                if (std::find(allowed.begin(), allowed.end(), choice) != allowed.end()) choices[name] = choice;
            } else if (toggles.count(name) && [value isKindOfClass:NSNumber.class]) {
                if (!includeWrites && isWriteFeature(name)) continue;
                toggles[name] = [value boolValue];
            } else if (numbers.count(name) && [value isKindOfClass:NSNumber.class]) {
                for (const Slider& slider : kSliders) {
                    if (name == slider.key) numbers[name] = std::clamp([value doubleValue], slider.low, slider.high);
                }
            }
        }
    }
};

// ---- Frame mailbox and presentation ------------------------------------------

struct ReceivedFrame {
    DisplayFrame packet;
    double received;
};

// Bounded mailbox: the main thread draws only the newest decoded frame.
// A busy UI thread must not replay a growing queue of old player positions.
class LatestFrameBuffer {
public:
    void publish(DisplayFrame packet) {
        std::lock_guard<std::mutex> guard(lock_);
        latest_ = ReceivedFrame{std::move(packet), uptime()};
        received_ += 1;
    }
    std::optional<ReceivedFrame> take() {
        std::lock_guard<std::mutex> guard(lock_);
        return std::exchange(latest_, std::nullopt);
    }
    void reject() {
        std::lock_guard<std::mutex> guard(lock_);
        rejected_ += 1;
    }
    std::pair<int, int> counts() {
        std::lock_guard<std::mutex> guard(lock_);
        return {received_, rejected_};
    }

private:
    std::mutex lock_;
    std::optional<ReceivedFrame> latest_;
    int received_ = 0, rejected_ = 0;
};

// Brief invalid camera reads do not erase an otherwise healthy frame. A valid
// empty frame still clears immediately; a stopped reader expires after 250 ms.
class FramePresentation {
public:
    std::optional<DisplayFrame> packet;
    std::optional<double> received;

    void reset() {
        packet.reset();
        received.reset();
        failure_.reset();
    }
    void accept(ReceivedFrame incoming) {
        if (!incoming.packet.complete) {
            failure_ = incoming.packet.status;
            return;
        }
        packet = std::move(incoming.packet);
        received = incoming.received;
        failure_.reset();
    }
    bool isFresh(double now) const {
        return received && now - *received >= 0 && now - *received < kFrameMaxAge;
    }
    std::string reason(double now) const {
        if (!isFresh(now)) return failure_.value_or("no fresh valid frame; targets hidden");
        if (failure_) return "brief camera read gap: " + *failure_;
        return packet && packet->targets.empty() ? "valid empty projected frame" : "drawing";
    }

private:
    std::optional<std::string> failure_;
};

struct AimGate {
    double residualX = 0, residualY = 0;

    std::optional<std::pair<int64_t, int64_t>> motion(const std::optional<AimStep>& step, bool enabled,
                                                      bool focused, bool held, bool trusted, double age) {
        if (!(enabled && focused && held && trusted && age >= 0 && age < kAimMaxAge && step
              && std::isfinite(step->dx) && std::isfinite(step->dy)
              && std::hypot(step->dx, step->dy) <= kAimMaxStep)) {
            reset();
            return std::nullopt;
        }
        residualX += step->dx;
        residualY += step->dy;
        int64_t dx = std::llround(residualX), dy = std::llround(residualY);
        residualX -= dx;
        residualY -= dy;
        if (dx == 0 && dy == 0) return std::nullopt;
        return std::make_pair(dx, dy);
    }
    void reset() { residualX = residualY = 0; }
};

std::optional<CGRect> gameBounds(int pid) {
    if (pid <= 0) return std::nullopt;
    CFArrayRef list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
                                                 kCGNullWindowID);
    if (list == nullptr) return std::nullopt;
    NSArray* entries = CFBridgingRelease(list);
    std::optional<CGRect> best;
    for (NSDictionary* entry in entries) {
        if ([entry[(id)kCGWindowOwnerPID] intValue] != pid || [entry[(id)kCGWindowLayer] intValue] != 0) continue;
        CGRect rect;
        if (!CGRectMakeWithDictionaryRepresentation((CFDictionaryRef)entry[(id)kCGWindowBounds], &rect)) continue;
        if (rect.size.width < 200 || rect.size.height < 150) continue;
        if (!best || rect.size.width * rect.size.height > best->size.width * best->size.height) best = rect;
    }
    return best;
}

}  // namespace

// ---- Windows ------------------------------------------------------------------

// Click-through while the menu is closed; becomes key only while it is open.
@interface OverlayWindow : NSWindow
@property(nonatomic) BOOL interactive;
@end

@implementation OverlayWindow
- (BOOL)canBecomeKeyWindow { return self.interactive; }
- (BOOL)canBecomeMainWindow { return NO; }
@end

@interface Overlay : NSObject <MTKViewDelegate>
@end

namespace {

int pid = 0;
double topInset = 28;
CGSize nudgeOffset = CGSizeZero;
bool menuOpen = false;
bool rightShiftDown = false;
bool windowAvailable = false;
bool presentable = false;  // Roblox or this menu is the active app
bool explorerRequested = false;
bool explorerSelected = false;
bool explorerExpandAll = false;
int explorerSnapshots = 0;
char explorerQuery[128] = "";
std::vector<ExpNode> explorerRoots, explorerVisible;
std::string explorerStatus = "Idle";
std::string keyboardNote, aimStatus = "Off";
double lastWindowPoll = 0, lastWindowSeen = 0, lastHealth = 0;
int previousReceived = 0, previousDraws = 0, drawCount = 0, spacePresses = 0;
bool spaceDown = false;
CGSize lastViewport = CGSizeZero;
Settings settings;
DisplayFrame panel;  // Latest controller availability/status, complete or not.
AimGate aimGate;
LatestFrameBuffer pendingFrames;
FramePresentation presentation;

OverlayWindow* window;
MTKView* metalView;
id<MTLCommandQueue> commandQueue;
NSStatusItem* statusItem;
Overlay* overlay;

NSRect fallbackFrame() { return NSScreen.mainScreen.visibleFrame; }

void setMenuOpen(bool open) {
    menuOpen = open;
    window.interactive = open;
    window.ignoresMouseEvents = !open;
    if (open) {
        if (!window.isVisible) {
            [window setFrame:fallbackFrame() display:NO];
            [window orderFrontRegardless];
        }
        [NSApp activate];
        [window makeKeyAndOrderFront:nil];
        return;
    }
    // Hand focus straight back so aim and input relay resume without a click.
    [window resignKeyWindow];
    if (pid > 0) [[NSRunningApplication runningApplicationWithProcessIdentifier:pid] activateWithOptions:0];
}

void saveState();

NSArray<NSString*>* soundFiles() {
    // macOS system sounds first, then the user's own files.
    NSMutableArray<NSString*>* files = [NSMutableArray array];
    NSString* system = @"/System/Library/Sounds";
    for (NSString* name in [[NSFileManager.defaultManager contentsOfDirectoryAtPath:system error:nil]
                               sortedArrayUsingSelector:@selector(compare:)]) {
        [files addObject:[system stringByAppendingPathComponent:name]];
    }
    NSString* custom = [[NSHomeDirectory() stringByAppendingPathComponent:@"Library/Application Support/WeirdExt"]
                           stringByAppendingPathComponent:@"sounds"];
    [NSFileManager.defaultManager createDirectoryAtPath:custom withIntermediateDirectories:YES attributes:nil error:nil];
    for (NSString* name in [[NSFileManager.defaultManager contentsOfDirectoryAtPath:custom error:nil]
                               sortedArrayUsingSelector:@selector(compare:)]) {
        if ([@[@"wav", @"mp3", @"aiff", @"aif", @"m4a", @"caf"] containsObject:name.pathExtension.lowercaseString]) {
            [files addObject:[custom stringByAppendingPathComponent:name]];
        }
    }
    return files;
}

NSArray<NSString*>* hitSounds = nil;
NSSound* hitPlayer = nil;

void playHitSound() {
    if (hitSounds == nil) hitSounds = soundFiles();
    if (hitSounds.count == 0) return;
    hitSound = std::clamp(hitSound, 0, (int)hitSounds.count - 1);
    [hitPlayer stop];
    hitPlayer = [[NSSound alloc] initWithContentsOfFile:hitSounds[hitSound] byReference:YES];
    hitPlayer.volume = (float)(hitVolume / 100.0);
    [hitPlayer play];
}
void applyStyle();

void quit() {
    for (const char* key : kWriteFeatures) settings.toggles[key] = false;
    emit(@{@"type": @"settings", @"settings": settings.snapshot()});
    saveState();
    emit(@{@"type": @"quit"});
    setMenuOpen(false);
}

void requestExplorer() {
    explorerStatus = "Requesting snapshot…";
    emit(@{@"type": @"explorer_refresh"});
}

void updateExplorer(ExpNode tree) {
    explorerSnapshots += 1;
    explorerStatus = "Snapshot " + std::to_string(explorerSnapshots) + " · updated";
    explorerRoots = {std::move(tree)};
    explorerVisible = filterTree(explorerRoots, explorerQuery);
}

// ---- Persistence and hotkeys -------------------------------------------------------

struct Bindable {
    const char* key;
    const char* label;
};

const Bindable kBindable[] = {{"esp_enabled", "ESP"}, {"aim_enabled", "Aimbot"}, {"fly", "Fly"},
                              {"noclip", "Noclip"}, {"infinite_jump", "Infinite Jump"},
                              {"walk_speed_enabled", "Speed"}, {"silent_aim", "Silent aim"}};

// Codes at kMouseBase + n are mouse button n; left click (n = 0) is never bindable.
constexpr int kMouseBase = 200;
constexpr int kRightMouse = kMouseBase + 1;

const std::pair<int, const char*> kKeyNames[] = {
    {kVK_ANSI_A, "A"}, {kVK_ANSI_B, "B"}, {kVK_ANSI_C, "C"}, {kVK_ANSI_D, "D"}, {kVK_ANSI_E, "E"},
    {kVK_ANSI_F, "F"}, {kVK_ANSI_G, "G"}, {kVK_ANSI_H, "H"}, {kVK_ANSI_I, "I"}, {kVK_ANSI_J, "J"},
    {kVK_ANSI_K, "K"}, {kVK_ANSI_L, "L"}, {kVK_ANSI_M, "M"}, {kVK_ANSI_N, "N"}, {kVK_ANSI_O, "O"},
    {kVK_ANSI_P, "P"}, {kVK_ANSI_Q, "Q"}, {kVK_ANSI_R, "R"}, {kVK_ANSI_S, "S"}, {kVK_ANSI_T, "T"},
    {kVK_ANSI_U, "U"}, {kVK_ANSI_V, "V"}, {kVK_ANSI_W, "W"}, {kVK_ANSI_X, "X"}, {kVK_ANSI_Y, "Y"},
    {kVK_ANSI_Z, "Z"}, {kVK_ANSI_0, "0"}, {kVK_ANSI_1, "1"}, {kVK_ANSI_2, "2"}, {kVK_ANSI_3, "3"},
    {kVK_ANSI_4, "4"}, {kVK_ANSI_5, "5"}, {kVK_ANSI_6, "6"}, {kVK_ANSI_7, "7"}, {kVK_ANSI_8, "8"},
    {kVK_ANSI_9, "9"}, {kVK_F1, "F1"}, {kVK_F2, "F2"}, {kVK_F3, "F3"}, {kVK_F4, "F4"}, {kVK_F5, "F5"},
    {kVK_F6, "F6"}, {kVK_F7, "F7"}, {kVK_F8, "F8"}, {kVK_F9, "F9"}, {kVK_F10, "F10"}, {kVK_F11, "F11"},
    {kVK_F12, "F12"}, {kVK_ANSI_Grave, "`"}, {kVK_ANSI_Minus, "-"}, {kVK_ANSI_Equal, "="},
    {kVK_ANSI_LeftBracket, "["}, {kVK_ANSI_RightBracket, "]"}, {kVK_ANSI_Semicolon, ";"},
    {kVK_ANSI_Quote, "'"}, {kVK_ANSI_Comma, ","}, {kVK_ANSI_Period, "."}, {kVK_ANSI_Slash, "/"},
    {kVK_ANSI_Backslash, "\\"}, {kVK_Tab, "Tab"}, {kVK_Space, "Space"},
    {kVK_Option, "Left Option"}, {kVK_RightOption, "Right Option"}, {kVK_Command, "Left Command"},
    {kVK_RightCommand, "Right Command"}, {kVK_Control, "Left Control"}, {kVK_RightControl, "Right Control"},
    {kVK_Shift, "Left Shift"}, {kMouseBase + 1, "Right Mouse"}, {kMouseBase + 2, "Middle Mouse"},
    {kMouseBase + 3, "Mouse 4"}, {kMouseBase + 4, "Mouse 5"}};

const char* keyName(int code) {
    for (const auto& [key, name] : kKeyNames) {
        if (key == code) return name;
    }
    return "?";
}

// CGEventSourceKeyState never reports modifiers; their device flag bits tell left from right.
const std::pair<int, uint64_t> kModifierMasks[] = {
    {kVK_Option, NX_DEVICELALTKEYMASK}, {kVK_RightOption, NX_DEVICERALTKEYMASK},
    {kVK_Command, NX_DEVICELCMDKEYMASK}, {kVK_RightCommand, NX_DEVICERCMDKEYMASK},
    {kVK_Control, NX_DEVICELCTLKEYMASK}, {kVK_RightControl, NX_DEVICERCTLKEYMASK},
    {kVK_Shift, NX_DEVICELSHIFTKEYMASK}};

bool keyDown(int code) {
    if (code >= kMouseBase) return (NSEvent.pressedMouseButtons >> (code - kMouseBase)) & 1;
    for (const auto& [key, mask] : kModifierMasks) {
        if (key == code) return CGEventSourceFlagsState(kCGEventSourceStateCombinedSessionState) & mask;
    }
    return CGEventSourceKeyState(kCGEventSourceStateCombinedSessionState, (CGKeyCode)code);
}

bool knownKey(int code) {
    return std::any_of(std::begin(kKeyNames), std::end(kKeyNames), [&](const auto& entry) { return entry.first == code; });
}

// Aim activation: Hold, Toggle or Always on the chosen key. Python only sees aim_held.
enum AimMode { AimHold, AimToggle, AimAlways };
int aimKey = kRightMouse;
int aimMode = AimHold;
bool aimToggled = false, aimKeyWasDown = false;
constexpr const char* kAimCapture = "aim_key";

std::map<std::string, int> binds;      // feature -> key code
std::map<std::string, bool> bindDown;  // edge detection per feature
std::string capturing;                 // feature waiting for a key; empty when idle
std::vector<int> capturingHeld;        // keys already down when capture started
bool restored = false;
bool stateDirty = false;
double lastSave = 0;

NSString* supportDirectory() {
    NSString* directory = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Application Support/WeirdExt"];
    [NSFileManager.defaultManager createDirectoryAtPath:directory withIntermediateDirectories:YES attributes:nil error:nil];
    return directory;
}

NSString* statePath() { return [supportDirectory() stringByAppendingPathComponent:@"settings.json"]; }

// Visual and aim tuning plus key binds persist; features that write game memory never do.
NSDictionary* stateDictionary() {
    NSMutableDictionary* bound = [NSMutableDictionary dictionary];
    for (const auto& [feature, code] : binds) bound[@(feature.c_str())] = @(code);
    NSDictionary* state = @{@"settings": settings.snapshot(false), @"binds": bound, @"aim_key": @(aimKey),
                            @"aim_mode": @(aimMode), @"accent": @(accentIndex), @"base": @(baseIndex),
                            @"watermark": @(showWatermark), @"hit_enabled": @(hitEnabled),
                            @"hit_mode": @(hitMode), @"hit_sound": @(hitSound), @"hit_volume": @(hitVolume)};
    return state;
}

// Returns the write error, or nil.
NSError* writeState(NSString* path) {
    NSData* data = [NSJSONSerialization dataWithJSONObject:stateDictionary()
                                                   options:NSJSONWritingPrettyPrinted error:nil];
    NSError* error = nil;
    [data writeToFile:path options:NSDataWritingAtomic error:&error];
    return error;
}

void saveState() {
    if (NSError* error = writeState(statePath())) {
        std::cerr << "[overlay] settings not saved: " << error.localizedDescription.UTF8String << std::endl;
    }
    stateDirty = false;
}

NSDictionary* readState(NSString* path) {
    NSData* data = [NSData dataWithContentsOfFile:path];
    if (data == nil) return nil;
    NSDictionary* state = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
    return [state isKindOfClass:NSDictionary.class] ? state : nil;
}

void applyState(NSDictionary* state) {
    if (NSDictionary* saved = object(state, @"settings")) settings.apply(saved, false);
    if (NSDictionary* saved = object(state, @"binds")) {
        for (const Bindable& feature : kBindable) {
            if (auto code = number(saved, @(feature.key)); code && knownKey((int)*code)) binds[feature.key] = (int)*code;
        }
    }
    if (auto code = number(state, @"aim_key"); code && knownKey((int)*code)) aimKey = (int)*code;
    if (auto mode = number(state, @"aim_mode"); mode && *mode >= AimHold && *mode <= AimAlways) aimMode = (int)*mode;
    if (auto index = number(state, @"accent"); index && *index >= 0 && *index < std::size(kAccents)) accentIndex = (int)*index;
    if (auto index = number(state, @"base"); index && *index >= 0 && *index < std::size(kBases)) baseIndex = (int)*index;
    if (state[@"watermark"]) showWatermark = flag(state, @"watermark");
    if (state[@"hit_enabled"]) hitEnabled = flag(state, @"hit_enabled");
    if (auto mode = number(state, @"hit_mode"); mode && (*mode == HitOnDamage || *mode == HitOnShoot)) hitMode = (int)*mode;
    if (auto index = number(state, @"hit_sound"); index && *index >= 0) hitSound = (int)*index;
    if (auto volume = number(state, @"hit_volume"); volume) hitVolume = std::clamp(*volume, 0.0, 100.0);
    applyStyle();
}

void loadState() {
    if (![NSFileManager.defaultManager fileExistsAtPath:statePath()]) return;
    NSDictionary* state = readState(statePath());
    if (state == nil) {
        std::cerr << "[overlay] ignoring unreadable " << statePath().UTF8String << std::endl;
        return;
    }
    applyState(state);
}

void settingsChanged() {
    emit(@{@"type": @"settings", @"settings": settings.snapshot()});
    stateDirty = true;
}

void pollHotkeys(bool focused, bool typing) {
    if (!capturing.empty()) {
        if (keyDown(kVK_Escape)) {
            if (capturing == kAimCapture) aimKey = kRightMouse;
            else binds.erase(capturing);
            capturing.clear();
            stateDirty = true;
            return;
        }
        for (const auto& [code, name] : kKeyNames) {
            bool held = std::find(capturingHeld.begin(), capturingHeld.end(), code) != capturingHeld.end();
            if (keyDown(code) && !held) {
                if (capturing == kAimCapture) {
                    aimKey = code;
                    aimKeyWasDown = true;  // the capturing press must not also toggle aim
                } else {
                    binds[capturing] = code;
                    bindDown[capturing] = true;  // the capturing press must not also toggle
                }
                capturing.clear();
                stateDirty = true;
                return;
            }
        }
        capturingHeld.erase(std::remove_if(capturingHeld.begin(), capturingHeld.end(),
                                           [](int code) { return !keyDown(code); }), capturingHeld.end());
        return;
    }
    for (const auto& [feature, code] : binds) {
        bool down = keyDown(code);
        if (down && !bindDown[feature] && focused && !typing) {
            settings.toggles[feature] = !settings.toggles[feature];
            settingsChanged();
        }
        bindDown[feature] = down;
    }
}

// ---- Overlay drawing ------------------------------------------------------------


// The Team's real TeamColor when known; otherwise the theme accent.
ImU32 teamColor(const std::optional<ImU32>& color) { return color.value_or(accentU32()); }

void drawLabel(ImDrawList* draw, ImVec2 anchor, bool above, const std::string& label, ImU32 color) {
    ImFont* font = ImGui::GetFont();
    ImVec2 size = font->CalcTextSizeA(kLabelSize, FLT_MAX, 0, label.c_str());
    ImVec2 pos(std::round(anchor.x - size.x / 2), std::round(above ? anchor.y - size.y - 4 : anchor.y + 3));
    draw->AddRectFilled(pos - ImVec2(4, 1), pos + size + ImVec2(4, 1), IM_COL32(0, 0, 0, 150), 3);
    draw->AddText(font, kLabelSize, pos, color, label.c_str());
}

void drawHealthBar(ImDrawList* draw, ImVec2 low, ImVec2 high, double health) {
    float fraction = (float)std::clamp(health, 0.0, 1.0);
    ImVec2 barLow(low.x - 6, low.y), barHigh(low.x - 3, high.y);
    draw->AddRectFilled(barLow - ImVec2(1, 1), barHigh + ImVec2(1, 1), kShadow);
    ImU32 color = ImGui::ColorConvertFloat4ToU32(ImVec4(1 - fraction, 0.25f + 0.65f * fraction, 0.25f, 1));
    draw->AddRectFilled(ImVec2(barLow.x, barHigh.y - (barHigh.y - barLow.y) * fraction), barHigh, color);
}

void drawArrow(ImDrawList* draw, ImVec2 center, float radius, const Offscreen& target, bool distances) {
    ImVec2 direction((float)std::cos(target.angle), (float)std::sin(target.angle));
    ImVec2 normal(-direction.y, direction.x);
    ImVec2 tip = center + direction * radius;
    ImVec2 base = tip - direction * 14;
    ImU32 color = teamColor(target.color);
    draw->AddTriangleFilled(tip + direction, base + normal * 8, base - normal * 8, kShadow);
    draw->AddTriangleFilled(tip, base + normal * 7, base - normal * 7, color);
    if (distances) drawLabel(draw, base - direction * 10, false, std::to_string((int)target.distance), color);
}

void drawWatermark(ImDrawList* draw, double now) {
    bool live = presentation.isFresh(now) && presentation.packet;
    char text[192];
    std::string extra = live ? std::to_string(presentation.packet->roster) + " players" : "waiting for game";
    for (const PlayerRow& player : panel.players) {
        if (panel.spectating && player.key == panel.spectating) extra += "   spectating " + player.name;
    }
    std::snprintf(text, sizeof text, "%.0f fps   %s", ImGui::GetIO().Framerate, extra.c_str());
    ImFont* font = ImGui::GetFont();
    float logoWidth = font->CalcTextSizeA(kLabelSize, FLT_MAX, 0, "WEIRDEXT").x;
    ImVec2 size = font->CalcTextSizeA(kLabelSize, FLT_MAX, 0, text);
    ImVec2 low(12, 12), high(12 + logoWidth + size.x + 34, 12 + size.y + 12);
    draw->AddRectFilled(low, high, IM_COL32(14, 15, 18, 225), 7);
    draw->AddRectFilled(low + ImVec2(7, 0), ImVec2(high.x - 7, low.y + 2), accentU32());
    draw->AddText(font, kLabelSize, low + ImVec2(10, 6), accentU32(), "WEIRDEXT");
    draw->AddText(font, kLabelSize, low + ImVec2(24 + logoWidth, 6), IM_COL32(205, 208, 216, 255), text);
}

// Cursor in the game view, 0..1 from the top-left, or nothing when it is outside it.
std::optional<ImVec2> cursorInView() {
    if (!window.isVisible) return std::nullopt;
    NSPoint local = [metalView convertPoint:[window convertPointFromScreen:NSEvent.mouseLocation] fromView:nil];
    NSSize area = metalView.bounds.size;
    if (local.x < 0 || local.y < 0 || local.x > area.width || local.y > area.height || area.width <= 0) {
        return std::nullopt;
    }
    return ImVec2((float)(local.x / area.width), (float)(1.0 - local.y / area.height));
}

void drawSilent(ImDrawList* draw, ImVec2 bounds, const DisplayFrame& frame) {
    if (!frame.silentAvailable || !frame.silentEnabled) return;
    std::optional<ImVec2> cursor = cursorInView();
    if (!cursor) return;
    ImVec2 origin = *cursor * bounds;
    ImU32 accent = accentU32();
    if (settings.toggles.at("silent_show_fov") && frame.silentRadius) {
        draw->AddCircle(origin, (float)*frame.silentRadius, (accent & 0x00FFFFFF) | (110u << 24), 96, 1.2f);
    }
    if (!frame.silentTarget) return;
    ImVec2 target((float)frame.silentTarget->x * bounds.x, (float)frame.silentTarget->y * bounds.y);
    draw->AddLine(origin, target, accent, 1.5f);
    draw->AddCircle(target, 6, accent, 24, 2);
    if (!frame.silentTarget->name.empty()) {
        draw->AddText(target + ImVec2(9, -7), accent, frame.silentTarget->name.c_str());
    }
}

void drawESP(ImDrawList* draw, ImVec2 bounds, double now) {
    if (showWatermark) drawWatermark(draw, now);
    RenderOptions options = presentation.packet ? presentation.packet->options : RenderOptions{};
    if (!options.enabled) return;
    ImVec2 center = bounds * 0.5f;
    if (options.centerMarker) {
        draw->AddLine(center - ImVec2(5, 0), center + ImVec2(6, 0), IM_COL32(255, 255, 255, 150));
        draw->AddLine(center - ImVec2(0, 5), center + ImVec2(0, 6), IM_COL32(255, 255, 255, 150));
    }
    if (!presentation.isFresh(now) || !presentation.packet) return;
    const DisplayFrame& frame = *presentation.packet;
    if (frame.aimEnabled && frame.aimRadius && *frame.aimRadius >= 20 && *frame.aimRadius <= 400) {
        draw->AddCircle(center, (float)*frame.aimRadius, IM_COL32(255, 255, 255, 72), 96, 1.0f);
    }
    drawSilent(draw, bounds, frame);
    // Overlay-center reference only. This does not validate camera pose/FOV,
    // and a custom game's crosshair need not be at the render-area center.
    if (options.centerMarker && frame.boresight) {
        auto [bx, by] = *frame.boresight;
        if (bx >= -0.05 && bx <= 1.05 && by >= -0.05 && by <= 1.05) {
            ImVec2 p((float)bx * bounds.x, (float)by * bounds.y);
            draw->AddQuadFilled(p - ImVec2(0, 7), p + ImVec2(7, 0), p + ImVec2(0, 7), p - ImVec2(7, 0),
                                IM_COL32(255, 255, 77, 255));
        }
    }
    for (const Marker& marker : frame.targets) {
        if (marker.distance < 0 || marker.distance >= 1e9 || marker.x < 0 || marker.x > 1
            || marker.y < 0 || marker.y > 1) continue;
        ImU32 color = teamColor(marker.color);
        ImVec2 p((float)marker.x * bounds.x, (float)marker.y * bounds.y);
        std::string distance = options.distances ? std::to_string((int)marker.distance) + " studs" : "";
        if (options.skeleton) {
            for (size_t i = 0; i + 3 < marker.bones.size(); i += 4) {
                ImVec2 a(marker.bones[i] * bounds.x, marker.bones[i + 1] * bounds.y);
                ImVec2 b(marker.bones[i + 2] * bounds.x, marker.bones[i + 3] * bounds.y);
                draw->AddLine(a, b, kShadow, 3.0f);
                draw->AddLine(a, b, IM_COL32(235, 235, 235, 230), 1.5f);
            }
        }
        if (marker.w && marker.h && *marker.w > 0.001 && *marker.h > 0.001) {
            ImVec2 half((float)*marker.w * bounds.x / 2, (float)*marker.h * bounds.y / 2);
            ImVec2 low = p - half, high = p + half;
            if (options.tracers) {
                draw->AddLine(ImVec2(center.x, bounds.y), ImVec2(p.x, high.y), kShadow, 2.5f);
                draw->AddLine(ImVec2(center.x, bounds.y), ImVec2(p.x, high.y), color, 1.0f);
            }
            if (options.boxes) {
                draw->AddRect(low, high, kShadow, 0, 0, 3.0f);
                draw->AddRect(low, high, color, 0, 0, 1.5f);
            }
            if (options.health && marker.health) drawHealthBar(draw, low, high, *marker.health);
            if (options.names && !marker.name.empty())
                drawLabel(draw, ImVec2(p.x, low.y), true, marker.name, IM_COL32_WHITE);
            if (!distance.empty()) drawLabel(draw, ImVec2(p.x, high.y), false, distance, IM_COL32(200, 200, 200, 255));
        } else {
            if (options.boxes) draw->AddCircleFilled(p, 3, color);
            if (options.names && !marker.name.empty()) drawLabel(draw, p - ImVec2(0, 6), true, marker.name, IM_COL32_WHITE);
            if (!distance.empty()) drawLabel(draw, p + ImVec2(0, 6), false, distance, IM_COL32(200, 200, 200, 255));
        }
    }
    if (options.offscreen) {
        float radius = std::min(bounds.x, bounds.y) * 0.42f;
        for (const Offscreen& target : frame.offscreen) drawArrow(draw, center, radius, target, options.distances);
    }
    // Join/leave feed: top-right pills, fading over four seconds.
    float y = 14;
    for (const Toast& toast : frame.toasts) {
        if (toast.age < 0 || toast.age >= kToastLifetime || toast.text.empty()) continue;
        int alpha = (int)(255 * std::clamp(1 - toast.age / kToastLifetime, 0.0, 1.0));
        ImVec2 size = ImGui::GetFont()->CalcTextSizeA(kLabelSize, FLT_MAX, 0, toast.text.c_str());
        ImVec2 pos(bounds.x - size.x - 22, y);
        draw->AddRectFilled(pos - ImVec2(8, 4), pos + size + ImVec2(8, 4), IM_COL32(10, 10, 10, alpha * 85 / 100), 6);
        draw->AddText(ImGui::GetFont(), kLabelSize, pos, (accentU32() & ~IM_COL32_A_MASK) | ((ImU32)alpha << IM_COL32_A_SHIFT),
                      toast.text.c_str());
        y += size.y + 14;
    }
}

// ---- Menu -------------------------------------------------------------------------

enum class Tab { Visuals, Player, Aim, Silent, Players, Misc, Keys, Theme, Configs, Explorer };

struct TabInfo {
    Tab tab;
    const char* label;
    const char* subtitle;
};

const TabInfo kTabs[] = {
    {Tab::Visuals, "Visuals", "ESP, filters and camera"},
    {Tab::Player, "Player", "Movement and physics"},
    {Tab::Aim, "Aim", "Target selection and smoothing"},
    {Tab::Silent, "Silent", "Hits without moving your camera"},
    {Tab::Players, "Players", "Teleport and spectate"},
    {Tab::Keys, "Keybinds", "Per-feature toggle keys"},
    {Tab::Misc, "Misc", "Hit sounds"},
    {Tab::Theme, "Theme", "Accent, background and overlay"},
    {Tab::Configs, "Configs", "Save and load setups"},
    {Tab::Explorer, "Explorer", "Read-only game tree"},
};

Tab currentTab = Tab::Visuals;

constexpr float kMenuWidth = 700, kMenuHeight = 480, kSidebarWidth = 168, kRowHeight = 28;
constexpr float kCardGap = 12, kMenuRounding = 12, kCardRounding = 9;
constexpr float kTitleSize = 21, kCaptionSize = 11.5f, kSmallSize = 12.5f, kLogoSize = 19;

const ImVec4 kText(0.93f, 0.94f, 0.97f, 1), kMuted(0.50f, 0.53f, 0.61f, 1), kTrack(1, 1, 1, 0.07f);
const ImVec4 kLine(1, 1, 1, 0.06f);

ImVec4 accentColor() { return ImGui::ColorConvertU32ToFloat4(accentU32()); }

ImVec4 mix(const ImVec4& a, const ImVec4& b, float t) {
    return ImVec4(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, a.w + (b.w - a.w) * t);
}

// GetColorU32 applies style alpha, so custom-drawn widgets dim inside BeginDisabled.
ImU32 tone(const ImVec4& color, float alpha = 1) {
    return ImGui::GetColorU32(ImVec4(color.x, color.y, color.z, color.w * alpha));
}

// Per-widget 0..1 easing toward on/off, kept in ImGui's state storage.
float animate(const char* key, bool on) {
    ImGuiStorage* storage = ImGui::GetStateStorage();
    ImGuiID id = ImGui::GetID(key);
    float target = on ? 1.0f : 0.0f;
    float value = storage->GetFloat(id, target);
    value += (target - value) * std::min(1.0f, ImGui::GetIO().DeltaTime * 16.0f);
    storage->SetFloat(id, value);
    return value;
}

void textAt(ImDrawList* draw, ImVec2 pos, float size, const ImVec4& color, const char* text) {
    draw->AddText(ImGui::GetFont(), size, pos, tone(color), text);
}

ImVec2 textSize(float size, const char* text) {
    return ImGui::GetFont()->CalcTextSizeA(size, FLT_MAX, 0, text);
}

bool switchRow(const char* id, const char* label, bool& value) {
    ImGui::PushID(id);
    ImVec2 pos = ImGui::GetCursorScreenPos();
    float width = ImGui::GetContentRegionAvail().x;
    bool clicked = ImGui::InvisibleButton("##toggle", ImVec2(width, kRowHeight));
    if (clicked) value = !value;
    bool hovered = ImGui::IsItemHovered();
    float t = animate("anim", value);
    ImDrawList* draw = ImGui::GetWindowDrawList();
    float mid = pos.y + kRowHeight / 2;
    textAt(draw, ImVec2(pos.x, mid - kFontSize / 2 - 1), kFontSize, hovered ? kText : mix(kText, kMuted, 0.25f), label);
    ImVec2 pill(34, 18), low(pos.x + width - pill.x, mid - pill.y / 2);
    draw->AddRectFilled(low, low + pill, tone(mix(kTrack, accentColor(), t)), pill.y / 2);
    float knob = low.x + pill.y / 2 + (pill.x - pill.y) * t;
    draw->AddCircleFilled(ImVec2(knob, mid), pill.y / 2 - 3, tone(ImVec4(1, 1, 1, 0.70f + 0.30f * t)));
    ImGui::PopID();
    return clicked;
}

bool toggle(const char* key, const char* label) {
    return switchRow(key, label, settings.toggles.at(key));
}

bool slider(const char* key, const char* label) {
    for (const Slider& entry : kSliders) {
        if (std::string(key) != entry.key) continue;
        double& value = settings.numbers.at(key);
        ImGui::PushID(key);
        ImVec2 pos = ImGui::GetCursorScreenPos();
        float width = ImGui::GetContentRegionAvail().x;
        ImGui::InvisibleButton("##slider", ImVec2(width, kFontSize + 20));
        bool active = ImGui::IsItemActive(), hovered = ImGui::IsItemHovered();
        bool changed = false;
        if (active) {
            float t = std::clamp((ImGui::GetIO().MousePos.x - pos.x) / width, 0.0f, 1.0f);
            double next = entry.low + t * (entry.high - entry.low);
            if (entry.integral) next = std::round(next);
            if (next != value) {
                value = next;
                changed = true;
            }
        }
        char number[32];
        std::snprintf(number, sizeof number, entry.integral ? "%.0f" : "%.2f", value);
        ImDrawList* draw = ImGui::GetWindowDrawList();
        textAt(draw, pos, kFontSize, kText, label);
        textAt(draw, ImVec2(pos.x + width - textSize(kFontSize, number).x, pos.y), kFontSize,
               active || hovered ? accentColor() : kMuted, number);
        float t = (float)((value - entry.low) / (entry.high - entry.low));
        float trackY = pos.y + kFontSize + 11;
        draw->AddRectFilled(ImVec2(pos.x, trackY - 2), ImVec2(pos.x + width, trackY + 2), tone(kTrack), 2);
        draw->AddRectFilled(ImVec2(pos.x, trackY - 2), ImVec2(pos.x + width * t, trackY + 2), tone(accentColor()), 2);
        ImVec2 knob(pos.x + width * t, trackY);
        draw->AddCircleFilled(knob, active || hovered ? 7.5f : 6.5f, tone(accentColor()));
        draw->AddCircleFilled(knob, active || hovered ? 4.0f : 3.5f, tone(ImVec4(1, 1, 1, 1)));
        ImGui::PopID();
        return changed;
    }
    throw std::logic_error(std::string("unknown slider ") + key);
}

bool segmentedIndex(const char* id, const char* label, std::initializer_list<const char*> labels, int& current) {
    ImGui::PushID(id);
    ImDrawList* draw = ImGui::GetWindowDrawList();
    ImVec2 pos = ImGui::GetCursorScreenPos();
    float width = ImGui::GetContentRegionAvail().x, height = 28;
    textAt(draw, pos, kFontSize, kText, label);
    pos.y += kFontSize + 8;
    draw->AddRectFilled(pos, pos + ImVec2(width, height), tone(kTrack), 7);
    float segment = width / (float)labels.size();
    bool changed = false;
    size_t index = 0;
    for (const char* option : labels) {
        ImVec2 low(pos.x + segment * index, pos.y);
        ImGui::SetCursorScreenPos(low);
        ImGui::PushID((int)index);
        bool clicked = ImGui::InvisibleButton("##segment", ImVec2(segment, height));
        bool hovered = ImGui::IsItemHovered();
        bool selected = current == (int)index;
        if (clicked && !selected) {
            current = (int)index;
            changed = selected = true;
        }
        float t = animate("anim", selected);
        draw->AddRectFilled(low + ImVec2(3, 3), low + ImVec2(segment - 3, height - 3),
                            tone(accentColor(), 0.9f * t), 5);
        ImVec2 size = textSize(kSmallSize, option);
        textAt(draw, low + ImVec2((segment - size.x) / 2, (height - size.y) / 2), kSmallSize,
               mix(hovered ? kText : kMuted, ImVec4(1, 1, 1, 1), t), option);
        ImGui::PopID();
        index += 1;
    }
    ImGui::SetCursorScreenPos(ImVec2(pos.x, pos.y + height));
    ImGui::Dummy(ImVec2(width, 2));
    ImGui::PopID();
    return changed;
}

// Segmented control for a settings choice; labels follow kChoices order.
bool segmented(const char* key, const char* label, std::initializer_list<const char*> labels) {
    const auto& values = kChoices.at(key);
    int current = (int)(std::find(values.begin(), values.end(), settings.choices[key]) - values.begin());
    if (!segmentedIndex(key, label, labels, current)) return false;
    settings.choices[key] = values.at(current);
    return true;
}

void startCapture(const char* target) {
    capturing = target;
    capturingHeld.clear();
    for (const auto& [code, name] : kKeyNames) {
        if (keyDown(code)) capturingHeld.push_back(code);
    }
}

// A labelled row with a key chip on the right; returns true when the row is clicked.
bool keyChipRow(const char* id, const char* label, const std::string& key, bool waiting, bool bound) {
    ImGui::PushID(id);
    ImDrawList* draw = ImGui::GetWindowDrawList();
    ImVec2 pos = ImGui::GetCursorScreenPos();
    float width = ImGui::GetContentRegionAvail().x, height = kRowHeight + 4;
    ImVec2 chip(std::max(64.0f, textSize(kSmallSize, key.c_str()).x + 22), 24);
    ImVec2 low(pos.x + width - chip.x, pos.y + (height - chip.y) / 2);
    bool clicked = ImGui::InvisibleButton("##chip", ImVec2(width, height));
    bool hovered = ImGui::IsItemHovered();
    textAt(draw, ImVec2(pos.x, pos.y + (height - kFontSize) / 2 - 1), kFontSize, kText, label);
    draw->AddRectFilled(low, low + chip, tone(waiting ? accentColor() : hovered ? mix(kTrack, accentColor(), 0.3f) : kTrack), 6);
    ImVec2 size = textSize(kSmallSize, key.c_str());
    textAt(draw, low + (chip - size) * 0.5f, kSmallSize, waiting || bound ? kText : kMuted, key.c_str());
    ImGui::PopID();
    return clicked;
}

void status(const std::string& message) {
    if (message.empty()) return;
    ImGui::PushFont(nullptr, kSmallSize);
    ImGui::PushStyleColor(ImGuiCol_Text, kMuted);
    ImGui::TextWrapped("%s", message.c_str());
    ImGui::PopStyleColor();
    ImGui::PopFont();
}

bool actionButton(const char* label) {
    ImGui::PushStyleColor(ImGuiCol_Button, kTrack);
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, mix(kTrack, accentColor(), 0.35f));
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, mix(kTrack, accentColor(), 0.6f));
    bool clicked = ImGui::Button(label, ImVec2(ImGui::GetContentRegionAvail().x, 30));
    ImGui::PopStyleColor(3);
    return clicked;
}

bool beginCard(const char* title, ImVec2 size) {
    ImGui::PushStyleColor(ImGuiCol_ChildBg, base().card);
    ImGui::PushStyleColor(ImGuiCol_Border, kLine);
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, kCardRounding);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(16, 14));
    bool open = ImGui::BeginChild(title, size, ImGuiChildFlags_Borders | ImGuiChildFlags_AlwaysUseWindowPadding);
    ImDrawList* draw = ImGui::GetWindowDrawList();
    ImVec2 pos = ImGui::GetCursorScreenPos();
    draw->AddRectFilled(pos + ImVec2(0, 3), pos + ImVec2(3, 3 + kCaptionSize - 2), tone(accentColor()), 1);
    textAt(draw, pos + ImVec2(10, 0), kCaptionSize, kMuted, title);
    ImGui::Dummy(ImVec2(0, kCaptionSize + 6));
    return open;
}

void endCard() {
    ImGui::EndChild();
    ImGui::PopStyleVar(2);
    ImGui::PopStyleColor(2);
}

void separator() {
    ImGui::Dummy(ImVec2(0, 2));
    ImVec2 pos = ImGui::GetCursorScreenPos();
    ImGui::GetWindowDrawList()->AddLine(pos, pos + ImVec2(ImGui::GetContentRegionAvail().x, 0), tone(kLine));
    ImGui::Dummy(ImVec2(0, 6));
}

std::optional<ExpNode> explorerChosen;

void drawExplorerNode(const ExpNode& node, int index, int depth) {
    ImGui::PushID(index);
    ImGuiTreeNodeFlags flags = ImGuiTreeNodeFlags_SpanAvailWidth | ImGuiTreeNodeFlags_OpenOnArrow
                             | ImGuiTreeNodeFlags_OpenOnDoubleClick;
    if (node.kids.empty()) flags |= ImGuiTreeNodeFlags_Leaf | ImGuiTreeNodeFlags_NoTreePushOnOpen;
    if (explorerChosen && explorerChosen->address == node.address) flags |= ImGuiTreeNodeFlags_Selected;
    if (explorerExpandAll) ImGui::SetNextItemOpen(true, ImGuiCond_Always);
    else if (depth == 0) ImGui::SetNextItemOpen(true, ImGuiCond_Once);
    bool open = ImGui::TreeNodeEx("##node", flags, "%s%s", node.name.c_str(), node.truncated ? " …" : "");
    if (ImGui::IsItemClicked() && !ImGui::IsItemToggledOpen()) {
        explorerChosen = ExpNode{node.name, node.cls, node.truncated, {}, node.address, node.parent};
        explorerChosen->kids.resize(node.kids.size());
    }
    ImGui::SameLine();
    ImGui::TextColored(kMuted, "%s", node.cls.c_str());
    if (open && !node.kids.empty()) {
        for (size_t i = 0; i < node.kids.size(); ++i) drawExplorerNode(node.kids[i], (int)i, depth + 1);
        ImGui::TreePop();
    }
    ImGui::PopID();
}

void copyRow(const char* label, const std::string& value) {
    ImGui::PushID(label);
    ImGui::TextColored(kMuted, "%s", label);
    ImGui::SameLine(80);
    ImGui::TextUnformatted(value.c_str());
    if (!value.empty() && value != "0x0") {
        ImGui::SameLine();
        if (ImGui::SmallButton("Copy")) ImGui::SetClipboardText(value.c_str());
    }
    ImGui::PopID();
}

void drawExplorer() {
    if (!explorerSelected) {
        explorerSelected = true;
        requestExplorer();
    }
    ImGui::PushStyleColor(ImGuiCol_FrameBg, kTrack);
    ImGui::SetNextItemWidth(-ImGui::CalcTextSize("Refresh").x - ImGui::GetStyle().FramePadding.x * 2
                            - ImGui::GetStyle().ItemSpacing.x);
    if (ImGui::InputTextWithHint("##filter", "Filter by name or class", explorerQuery, sizeof explorerQuery)) {
        explorerVisible = filterTree(explorerRoots, explorerQuery);
        explorerExpandAll = explorerQuery[0] != 0;
    }
    ImGui::PopStyleColor();
    ImGui::SameLine();
    if (ImGui::Button("Refresh")) requestExplorer();
    status(explorerStatus);
    float details = explorerChosen ? ImGui::GetTextLineHeightWithSpacing() * 5 + 12 : 0;
    ImGui::PushStyleColor(ImGuiCol_ChildBg, base().card);
    ImGui::PushStyleColor(ImGuiCol_Border, kLine);
    ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, kCardRounding);
    if (ImGui::BeginChild("tree", ImVec2(0, -details), ImGuiChildFlags_Borders)) {
        for (size_t i = 0; i < explorerVisible.size(); ++i) drawExplorerNode(explorerVisible[i], (int)i, 0);
    }
    ImGui::EndChild();
    ImGui::PopStyleVar();
    ImGui::PopStyleColor(2);
    if (explorerChosen) {
        ImGui::Dummy(ImVec2(0, 4));
        copyRow("Name", explorerChosen->name);
        copyRow("Class", explorerChosen->cls);
        copyRow("Address", explorerChosen->address);
        copyRow("Parent", explorerChosen->parent);
        copyRow("Children", std::to_string(explorerChosen->kids.size()) + (explorerChosen->truncated ? "+" : ""));
    }
    explorerExpandAll = false;
}

void drawKeys(float height) {
    beginCard("KEYBINDS", ImVec2(0, height));
    status("Click a feature, then press a key, Option/Command/Control, or a mouse side button. "
           "Esc clears. Keys toggle while Roblox is focused.");
    ImGui::Dummy(ImVec2(0, 4));
    for (const Bindable& feature : kBindable) {
        bool waiting = capturing == feature.key;
        bool bound = binds.count(feature.key) > 0;
        std::string key = waiting ? "Press a key…" : bound ? keyName(binds[feature.key]) : "None";
        if (keyChipRow(feature.key, feature.label, key, waiting, bound) && !waiting) startCapture(feature.key);
    }
    separator();
    status("Right Shift always toggles this menu. The aim key lives on the Aim tab.");
    endCard();
}

// Two cards side by side; the right column may be split into two stacked cards.
struct Columns {
    float left, right, height;
};

Columns columns() {
    ImVec2 available = ImGui::GetContentRegionAvail();
    float half = (available.x - kCardGap) / 2;
    return {half, half, available.y};
}

bool drawVisuals() {
    bool changed = false;
    Columns layout = columns();
    beginCard("ESP", ImVec2(layout.left, layout.height));
    changed |= toggle("esp_enabled", "Enable ESP");
    separator();
    changed |= toggle("boxes", "Boxes");
    changed |= toggle("names", "Names");
    changed |= toggle("distances", "Distance");
    changed |= toggle("esp_skeleton", "Skeleton");
    changed |= toggle("esp_tracers", "Tracers");
    changed |= toggle("esp_health", "Health bars");
    changed |= toggle("esp_offscreen", "Off-screen arrows");
    separator();
    changed |= slider("box_height", "Fallback height");
    changed |= slider("box_ratio", "Fallback width");
    endCard();
    ImGui::SameLine(0, kCardGap);
    ImGui::BeginGroup();
    float top = (layout.height - kCardGap) * 0.52f;
    beginCard("FILTERS", ImVec2(layout.right, top));
    changed |= toggle("team_check", "Hide teammates");
    changed |= toggle("show_local", "Show me");
    changed |= toggle("center_marker", "Center mark");
    changed |= slider("fps", "Update rate");
    endCard();
    ImGui::Dummy(ImVec2(0, kCardGap - ImGui::GetStyle().ItemSpacing.y));
    beginCard("CAMERA", ImVec2(layout.right, layout.height - top - kCardGap));
    ImGui::BeginDisabled(!panel.cameraAvailable);
    changed |= toggle("fov_enabled", "Change FOV");
    ImGui::EndDisabled();
    changed |= slider("fov", "Field of view");
    status(panel.cameraStatus);
    endCard();
    ImGui::EndGroup();
    return changed;
}

bool drawPlayer() {
    bool changed = false;
    Columns layout = columns();
    beginCard("MOVEMENT", ImVec2(layout.left, layout.height));
    ImGui::BeginDisabled(!panel.movementAvailable);
    changed |= toggle("walk_speed_enabled", "Walk speed");
    ImGui::EndDisabled();
    changed |= slider("walk_speed", "Speed");
    separator();
    ImGui::BeginDisabled(!panel.movementAvailable);
    changed |= toggle("jump_power_enabled", "Jump power");
    ImGui::EndDisabled();
    changed |= slider("jump_power", "Power");
    status(panel.movementStatus);
    endCard();
    ImGui::SameLine(0, kCardGap);
    beginCard("PHYSICS", ImVec2(layout.right, layout.height));
    ImGui::BeginDisabled(!panel.noclipAvailable);
    changed |= toggle("noclip", "Noclip");
    changed |= toggle("infinite_jump", "Infinite jump");
    changed |= toggle("fly", "Fly");
    ImGui::EndDisabled();
    changed |= slider("fly_speed", "Fly speed");
    status("Fly: WASD follows the camera · Space rises · Left Shift sinks.");
    status(panel.noclipStatus);
    separator();
    if (actionButton("Allow keyboard input…")) {
        keyboardNote = CGRequestListenEventAccess() ? "Keyboard input allowed"
                                                    : "Enable WeirdExt in Input Monitoring, then restart.";
    }
    status(keyboardNote);
    endCard();
    return changed;
}

bool drawAim() {
    bool changed = false;
    Columns layout = columns();
    beginCard("AIMBOT", ImVec2(layout.left, layout.height));
    changed |= toggle("aim_enabled", "Enable aimbot");
    changed |= toggle("aim_sticky", "Sticky target");
    changed |= toggle("aim_health_check", "Health check");
    if (settings.toggles.at("aim_health_check")) changed |= slider("aim_health_value", "Max target health");
    separator();
    changed |= segmented("aim_method", "Method", {"Mouse", "Camera"});
    changed |= segmented("aim_part", "Target part", {"Head", "Torso", "Closest"});
    changed |= segmented("aim_priority", "Priority", {"Crosshair", "Distance"});
    endCard();
    ImGui::SameLine(0, kCardGap);
    beginCard("TUNING", ImVec2(layout.right, layout.height));
    bool waiting = capturing == kAimCapture;
    if (keyChipRow("aim_key", "Aim key", waiting ? "Press a key…" : keyName(aimKey), waiting, true) && !waiting) {
        startCapture(kAimCapture);
    }
    if (segmentedIndex("aim_mode", "Activation", {"Hold", "Toggle", "Always"}, aimMode)) {
        aimToggled = false;
        stateDirty = true;
    }
    separator();
    changed |= slider("aim_radius", "FOV radius");
    changed |= slider("aim_smoothing", "Smoothness");
    status("Esc while choosing resets the aim key to Right Mouse. Hide teammates, target part, priority "
           "and the health check apply to the aimbot and silent aim.");
    separator();
    if (actionButton("Allow mouse control…")) {
        NSDictionary* options = @{(__bridge NSString*)kAXTrustedCheckOptionPrompt: @YES};
        AXIsProcessTrustedWithOptions((__bridge CFDictionaryRef)options);
    }
    status(aimStatus);
    endCard();
    return changed;
}

bool drawSilentTab() {
    bool changed = false;
    Columns layout = columns();
    beginCard("SILENT AIM", ImVec2(layout.left, layout.height));
    ImGui::BeginDisabled(!panel.silentAvailable);
    changed |= toggle("silent_aim", "Enable silent aim");
    ImGui::EndDisabled();
    status(panel.silentAvailable ? panel.silentStatus : "Needs probe_offsets.py viewport.");
    separator();
    changed |= toggle("silent_show_fov", "Show FOV");
    changed |= slider("silent_radius", "FOV radius");
    status("The circle follows your cursor. A line marks the target your shots are redirected to.");
    endCard();
    ImGui::SameLine(0, kCardGap);
    beginCard("METHOD", ImVec2(layout.right, layout.height));
    status("Viewport: stretches the camera's viewport size so the cursor's ray hits the target. Works "
           "with guns that aim via Mouse.Hit, Mouse.Target or Camera:ScreenPointToRay.");
    separator();
    status("Guns that raycast from the camera's look direction, or that the server re-checks, ignore it. "
           "UI may shift while a target is held.");
    separator();
    status("Target part, priority, hide teammates and the health check come from the Aim tab.");
    endCard();
    return changed;
}

// ---- Players: selection-first list with Roblox avatars -----------------------------

// Fetched once per username from Roblox's public APIs: username -> user id and
// display name, then the 150x150 headshot. Nothing else leaves this process.
struct Avatar {
    std::string displayName;
    id<MTLTexture> texture = nil;
};

std::map<std::string, Avatar> avatars;
std::vector<std::string> avatarQueue;
double lastAvatarBatch = 0;
id<MTLDevice> metalDevice;
long long selectedPlayer = 0;
int playerSort = 0;  // 0 = name, 1 = distance
char playerQuery[64] = "";
constexpr double kAvatarBatchSeconds = 0.5;
constexpr size_t kAvatarBatchSize = 50;

id<MTLTexture> textureFromImage(NSData* data) {
    CGImageSourceRef source = CGImageSourceCreateWithData((__bridge CFDataRef)data, nullptr);
    if (source == nullptr) return nil;
    CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, nullptr);
    CFRelease(source);
    if (image == nullptr) return nil;
    size_t width = CGImageGetWidth(image), height = CGImageGetHeight(image);
    std::vector<uint8_t> pixels(width * height * 4);
    CGColorSpaceRef space = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(pixels.data(), width, height, 8, width * 4, space,
                                                 kCGImageAlphaPremultipliedLast);
    CGColorSpaceRelease(space);
    CGContextDrawImage(context, CGRectMake(0, 0, width, height), image);
    CGContextRelease(context);
    CGImageRelease(image);
    MTLTextureDescriptor* descriptor = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm
                                                                                         width:width height:height
                                                                                     mipmapped:NO];
    id<MTLTexture> texture = [metalDevice newTextureWithDescriptor:descriptor];
    [texture replaceRegion:MTLRegionMake2D(0, 0, width, height) mipmapLevel:0 withBytes:pixels.data()
               bytesPerRow:width * 4];
    return texture;
}

void fetchJSON(NSURLRequest* request, void (^done)(NSDictionary*)) {
    [[NSURLSession.sharedSession dataTaskWithRequest:request
                                   completionHandler:^(NSData* data, NSURLResponse*, NSError* error) {
        NSDictionary* body = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
        if (error != nil || ![body isKindOfClass:NSDictionary.class]) {
            std::cerr << "[overlay] avatar lookup failed: "
                      << (error ? error.localizedDescription.UTF8String : "unexpected response") << std::endl;
            return;
        }
        done(body);
    }] resume];
}

void requestAvatars(std::vector<std::string> names) {
    NSMutableArray* usernames = [NSMutableArray array];
    for (const std::string& name : names) [usernames addObject:@(name.c_str())];
    NSMutableURLRequest* lookup = [NSMutableURLRequest requestWithURL:
        [NSURL URLWithString:@"https://users.roblox.com/v1/usernames/users"]];
    lookup.HTTPMethod = @"POST";
    [lookup setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
    lookup.HTTPBody = [NSJSONSerialization dataWithJSONObject:@{@"usernames": usernames, @"excludeBannedUsers": @NO}
                                                      options:0 error:nil];
    fetchJSON(lookup, ^(NSDictionary* users) {
        NSMutableDictionary<NSString*, NSString*>* nameById = [NSMutableDictionary dictionary];
        for (NSDictionary* user in users[@"data"]) {
            if (![user isKindOfClass:NSDictionary.class] || ![user[@"id"] isKindOfClass:NSNumber.class]) continue;
            NSString* requested = user[@"requestedUsername"], *display = user[@"displayName"];
            if (![requested isKindOfClass:NSString.class]) continue;
            nameById[[user[@"id"] stringValue]] = requested;
            std::string key = requested.UTF8String, shown = [display isKindOfClass:NSString.class] ? display.UTF8String : "";
            dispatch_async(dispatch_get_main_queue(), ^{ avatars[key].displayName = shown; });
        }
        if (nameById.count == 0) return;
        NSString* ids = [nameById.allKeys componentsJoinedByString:@","];
        NSURL* url = [NSURL URLWithString:[NSString stringWithFormat:
            @"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=%@&size=150x150&format=Png&isCircular=false", ids]];
        fetchJSON([NSURLRequest requestWithURL:url], ^(NSDictionary* thumbnails) {
            for (NSDictionary* entry in thumbnails[@"data"]) {
                if (![entry isKindOfClass:NSDictionary.class] || ![entry[@"state"] isEqual:@"Completed"]) continue;
                NSString* username = nameById[[entry[@"targetId"] stringValue]];
                NSString* imageUrl = entry[@"imageUrl"];
                if (username == nil || ![imageUrl isKindOfClass:NSString.class]) continue;
                std::string key = username.UTF8String;
                [[NSURLSession.sharedSession dataTaskWithURL:[NSURL URLWithString:imageUrl]
                                           completionHandler:^(NSData* data, NSURLResponse*, NSError* error) {
                    id<MTLTexture> texture = (data && !error) ? textureFromImage(data) : nil;
                    if (texture != nil) dispatch_async(dispatch_get_main_queue(), ^{ avatars[key].texture = texture; });
                }] resume];
            }
        });
    });
}

void pollAvatars(double now) {
    for (const PlayerRow& player : panel.players) {
        if (avatars.count(player.name)) continue;
        avatars[player.name] = Avatar{};
        avatarQueue.push_back(player.name);
    }
    if (avatarQueue.empty() || now - lastAvatarBatch < kAvatarBatchSeconds) return;
    lastAvatarBatch = now;
    size_t count = std::min(avatarQueue.size(), kAvatarBatchSize);
    requestAvatars(std::vector<std::string>(avatarQueue.begin(), avatarQueue.begin() + count));
    avatarQueue.erase(avatarQueue.begin(), avatarQueue.begin() + count);
}

std::string displayNameOf(const PlayerRow& player) {
    auto found = avatars.find(player.name);
    return found != avatars.end() && !found->second.displayName.empty() ? found->second.displayName : player.name;
}

void drawAvatar(ImDrawList* draw, ImVec2 low, float size, const PlayerRow& player) {
    ImVec2 high = low + ImVec2(size, size), center = low + ImVec2(size, size) * 0.5f;
    draw->AddCircleFilled(center, size / 2, tone(mix(kTrack, accentColor(), 0.15f)), 48);
    auto found = avatars.find(player.name);
    if (found != avatars.end() && found->second.texture != nil) {
        ImTextureID texture = (ImTextureID)(uintptr_t)(__bridge void*)found->second.texture;
        draw->AddImageRounded(texture, low, high, ImVec2(0, 0), ImVec2(1, 1), tone(ImVec4(1, 1, 1, 1)), size / 2);
    } else {
        std::string initial = displayNameOf(player).substr(0, 1);
        float textSizePx = size * 0.42f;
        ImVec2 extent = textSize(textSizePx, initial.c_str());
        textAt(draw, center - extent * 0.5f, textSizePx, kText, initial.c_str());
    }
    // Team ring so colors read at a glance in the list.
    if (player.color) draw->AddCircle(center, size / 2 + 1.5f, *player.color, 48, 2);
}

bool wideButton(const char* id, const char* label, bool primary, bool enabled) {
    ImVec2 low = ImGui::GetCursorScreenPos();
    ImVec2 size(ImGui::GetContentRegionAvail().x, 34);
    ImGui::BeginDisabled(!enabled);
    bool clicked = ImGui::InvisibleButton(id, size);
    bool hovered = ImGui::IsItemHovered();
    ImGui::EndDisabled();
    ImVec4 fill = primary ? accentColor() : kTrack;
    if (hovered) fill = primary ? mix(accentColor(), ImVec4(1, 1, 1, 1), 0.15f) : mix(kTrack, accentColor(), 0.35f);
    float alpha = enabled ? 1.0f : 0.35f;
    ImDrawList* draw = ImGui::GetWindowDrawList();
    draw->AddRectFilled(low, low + size, tone(fill, alpha), 8);
    ImVec2 extent = textSize(kFontSize, label);
    textAt(draw, low + (size - extent) * 0.5f, kFontSize, ImVec4(1, 1, 1, alpha), label);
    return clicked && enabled;
}

void playerAction(const char* action, long long key) {
    emit(@{@"type": @"player_action", @"action": @(action), @"key": @(key)});
}

std::vector<const PlayerRow*> visiblePlayers() {
    std::vector<const PlayerRow*> rows;
    for (const PlayerRow& player : panel.players) {
        if (playerQuery[0] == 0 || containsCaseless(player.name, playerQuery)
            || containsCaseless(displayNameOf(player), playerQuery)) {
            rows.push_back(&player);
        }
    }
    // Name order never shuffles under the cursor; distance order is opt-in.
    std::stable_sort(rows.begin(), rows.end(), [](const PlayerRow* a, const PlayerRow* b) {
        if (playerSort == 1) return a->distance < b->distance;
        return [@(displayNameOf(*a).c_str()) localizedCaseInsensitiveCompare:@(displayNameOf(*b).c_str())]
               == NSOrderedAscending;
    });
    return rows;
}

void drawPlayerList(float width, float height) {
    beginCard("PLAYERS", ImVec2(width, height));
    ImGui::PushStyleColor(ImGuiCol_FrameBg, kTrack);
    ImGui::SetNextItemWidth(-FLT_MIN);
    ImGui::InputTextWithHint("##player_search", "Search players", playerQuery, sizeof playerQuery);
    ImGui::PopStyleColor();
    segmentedIndex("player_sort", "Sort by", {"Name", "Distance"}, playerSort);
    ImGui::Dummy(ImVec2(0, 2));
    auto rows = visiblePlayers();
    if (rows.empty()) status(panel.players.empty() ? "No other players with a readable character yet."
                                                   : "No players match the search.");
    ImDrawList* draw = ImGui::GetWindowDrawList();
    constexpr float rowHeight = 46, avatarSize = 32;
    for (const PlayerRow* player : rows) {
        ImGui::PushID((int)(player->key & 0x7fffffff));
        ImVec2 pos = ImGui::GetCursorScreenPos();
        float rowWidth = ImGui::GetContentRegionAvail().x;
        if (ImGui::InvisibleButton("##row", ImVec2(rowWidth, rowHeight - 4))) selectedPlayer = player->key;
        bool hovered = ImGui::IsItemHovered();
        bool selected = selectedPlayer == player->key;
        float t = animate("anim", selected);
        if (t > 0.01f) draw->AddRectFilled(pos, pos + ImVec2(rowWidth, rowHeight - 4), tone(accentColor(), 0.16f * t), 8);
        else if (hovered) draw->AddRectFilled(pos, pos + ImVec2(rowWidth, rowHeight - 4), tone(ImVec4(1, 1, 1, 0.035f)), 8);
        drawAvatar(draw, pos + ImVec2(6, (rowHeight - 4 - avatarSize) / 2), avatarSize, *player);
        std::string shown = displayNameOf(*player), handle = "@" + player->name;
        textAt(draw, pos + ImVec2(48, 5), kFontSize, kText, shown.c_str());
        textAt(draw, pos + ImVec2(48, 6 + kFontSize + 2), kSmallSize, kMuted, handle.c_str());
        char distance[24];
        std::snprintf(distance, sizeof distance, "%.0f", player->distance);
        ImVec2 extent = textSize(kSmallSize, distance);
        textAt(draw, ImVec2(pos.x + rowWidth - extent.x - 8, pos.y + (rowHeight - 4 - kSmallSize) / 2), kSmallSize,
               kMuted, distance);
        if (panel.spectating == player->key) {
            draw->AddCircleFilled(ImVec2(pos.x + rowWidth - extent.x - 18, pos.y + (rowHeight - 4) / 2), 3, accentU32());
        }
        ImGui::SetCursorScreenPos(pos + ImVec2(0, rowHeight));
        ImGui::Dummy(ImVec2(rowWidth, 0));
        ImGui::PopID();
    }
    endCard();
}

void drawSelectedPlayer(float width, float height) {
    beginCard("SELECTED", ImVec2(width, height));
    auto found = std::find_if(panel.players.begin(), panel.players.end(),
                              [](const PlayerRow& player) { return player.key == selectedPlayer; });
    ImDrawList* draw = ImGui::GetWindowDrawList();
    float inner = ImGui::GetContentRegionAvail().x;
    if (found == panel.players.end()) {
        status(selectedPlayer ? "That player left or is no longer readable." : "Select a player from the list.");
    } else {
        const PlayerRow& player = *found;
        constexpr float avatarSize = 84;
        ImVec2 pos = ImGui::GetCursorScreenPos();
        drawAvatar(draw, pos + ImVec2((inner - avatarSize) / 2, 2), avatarSize, player);
        ImGui::Dummy(ImVec2(inner, avatarSize + 8));
        std::string shown = displayNameOf(player), handle = "@" + player.name;
        pos = ImGui::GetCursorScreenPos();
        ImVec2 extent = textSize(17, shown.c_str());
        textAt(draw, pos + ImVec2((inner - extent.x) / 2, 0), 17, kText, shown.c_str());
        extent = textSize(kSmallSize, handle.c_str());
        textAt(draw, pos + ImVec2((inner - extent.x) / 2, 22), kSmallSize, kMuted, handle.c_str());
        ImGui::Dummy(ImVec2(inner, 40));
        separator();
        char line[48];
        std::snprintf(line, sizeof line, "%.0f studs", player.distance);
        pos = ImGui::GetCursorScreenPos();
        textAt(draw, pos, kSmallSize, kMuted, "Distance");
        textAt(draw, pos + ImVec2(inner - textSize(kSmallSize, line).x, 0), kSmallSize, kText, line);
        ImGui::Dummy(ImVec2(inner, kSmallSize + 6));
        pos = ImGui::GetCursorScreenPos();
        const char* team = player.team == 0 ? "None" : player.teammate ? "Teammate" : "Enemy";
        textAt(draw, pos, kSmallSize, kMuted, "Team");
        textAt(draw, pos + ImVec2(inner - textSize(kSmallSize, team).x, 0), kSmallSize,
               player.color ? ImGui::ColorConvertU32ToFloat4(*player.color) : kText, team);
        ImGui::Dummy(ImVec2(inner, kSmallSize + 6));
        if (player.health) {
            pos = ImGui::GetCursorScreenPos();
            float fraction = (float)std::clamp(*player.health, 0.0, 1.0);
            textAt(draw, pos, kSmallSize, kMuted, "Health");
            float bar = inner * 0.5f;
            ImVec2 low(pos.x + inner - bar, pos.y + kSmallSize / 2 - 2);
            draw->AddRectFilled(low, low + ImVec2(bar, 5), tone(kTrack), 3);
            draw->AddRectFilled(low, low + ImVec2(bar * fraction, 5),
                                tone(ImVec4(1 - fraction, 0.25f + 0.65f * fraction, 0.25f, 1)), 3);
            ImGui::Dummy(ImVec2(inner, kSmallSize + 6));
        }
        separator();
        bool watching = panel.spectating == player.key;
        if (wideButton("##teleport", "Teleport", true, panel.teleportAvailable)) playerAction("teleport", player.key);
        if (wideButton("##spectate", watching ? "Stop spectating" : "Spectate", watching, panel.spectateAvailable)) {
            playerAction(watching ? "stop_spectate" : "spectate", player.key);
        }
    }
    status(panel.playerStatus);
    if (!panel.teleportAvailable) status("Teleport needs probe_offsets.py teleport.");
    if (!panel.spectateAvailable) status("Spectate needs probe_offsets.py subject.");
    endCard();
}

void drawPlayers() {
    ImVec2 available = ImGui::GetContentRegionAvail();
    float list = (available.x - kCardGap) * 0.56f;
    drawPlayerList(list, available.y);
    ImGui::SameLine(0, kCardGap);
    drawSelectedPlayer(available.x - list - kCardGap, available.y);
}

void drawMisc() {
    Columns layout = columns();
    beginCard("HIT SOUNDS", ImVec2(layout.left, layout.height));
    if (switchRow("hit_enabled", "Hit sounds", hitEnabled)) stateDirty = true;
    if (segmentedIndex("hit_mode", "Play on", {"Damage", "Shoot"}, hitMode)) stateDirty = true;
    status(hitMode == HitOnDamage ? "An enemy loses health right after you click."
                                  : "Every left click while Roblox is focused.");
    separator();
    double low = 0, high = 100;
    ImGui::PushID("hit_volume");
    ImGui::SetNextItemWidth(-FLT_MIN);
    if (ImGui::SliderScalar("##volume", ImGuiDataType_Double, &hitVolume, &low, &high, "Volume %.0f%%")) stateDirty = true;
    ImGui::PopID();
    if (actionButton("Preview")) playHitSound();
    endCard();
    ImGui::SameLine(0, kCardGap);
    beginCard("SOUND", ImVec2(layout.right, layout.height));
    if (hitSounds == nil) hitSounds = soundFiles();
    for (NSUInteger index = 0; index < hitSounds.count; ++index) {
        bool selected = (int)index == hitSound;
        if (ImGui::Selectable(hitSounds[index].lastPathComponent.stringByDeletingPathExtension.UTF8String, selected)) {
            hitSound = (int)index;
            stateDirty = true;
            playHitSound();
        }
    }
    separator();
    status("Add your own .wav/.mp3/.aiff to ~/Library/Application Support/WeirdExt/sounds");
    if (actionButton("Open sounds folder")) {
        [NSWorkspace.sharedWorkspace openURL:[NSURL fileURLWithPath:[[NSHomeDirectory()
            stringByAppendingPathComponent:@"Library/Application Support/WeirdExt"] stringByAppendingPathComponent:@"sounds"]]];
    }
    if (actionButton("Refresh list")) hitSounds = soundFiles();
    endCard();
}

// ---- Configs: named snapshots of everything settings.json keeps --------------------

char configName[33] = "";
NSArray<NSString*>* configList;
std::string configSelected, configStatus;

NSString* configDirectory() {
    NSString* directory = [supportDirectory() stringByAppendingPathComponent:@"configs"];
    [NSFileManager.defaultManager createDirectoryAtPath:directory withIntermediateDirectories:YES attributes:nil error:nil];
    return directory;
}

NSString* configPath(const std::string& name) {
    return [configDirectory() stringByAppendingPathComponent:[@(name.c_str()) stringByAppendingPathExtension:@"json"]];
}

NSArray<NSString*>* listConfigs() {
    NSMutableArray* names = [NSMutableArray array];
    for (NSString* file in [NSFileManager.defaultManager contentsOfDirectoryAtPath:configDirectory() error:nil]) {
        if ([file.pathExtension isEqualToString:@"json"]) [names addObject:file.stringByDeletingPathExtension];
    }
    return [names sortedArrayUsingSelector:@selector(localizedCaseInsensitiveCompare:)];
}

// Letters, digits, spaces, '-' and '_' only, so a name can never leave the configs folder.
std::string cleanConfigName(const char* raw) {
    std::string name;
    for (const char* c = raw; *c; ++c) {
        if (std::isalnum((unsigned char)*c) || *c == ' ' || *c == '-' || *c == '_') name += *c;
    }
    size_t first = name.find_first_not_of(' '), last = name.find_last_not_of(' ');
    return first == std::string::npos ? "" : name.substr(first, last - first + 1);
}

bool drawConfigs() {
    bool changed = false;
    if (configList == nil) configList = listConfigs();
    Columns layout = columns();
    beginCard("SAVE", ImVec2(layout.left, layout.height));
    ImGui::SetNextItemWidth(-FLT_MIN);
    bool entered = ImGui::InputTextWithHint("##config_name", "Config name", configName, sizeof configName,
                                            ImGuiInputTextFlags_EnterReturnsTrue);
    if (actionButton("Save config") || entered) {
        std::string name = cleanConfigName(configName);
        if (name.empty()) {
            configStatus = "Type a name first (letters, numbers, spaces, - and _).";
        } else if (NSError* error = writeState(configPath(name))) {
            configStatus = std::string("Not saved: ") + error.localizedDescription.UTF8String;
        } else {
            configStatus = "Saved \"" + name + "\"";
            configSelected = name;
            configList = listConfigs();
        }
    }
    status("Saves visuals, aim tuning, silent FOV, key binds, theme and hit sounds. Features that write "
           "game memory (speed, fly, aimbot, silent aim…) are never switched on by a config.");
    separator();
    if (actionButton("Open configs folder")) {
        [NSWorkspace.sharedWorkspace openURL:[NSURL fileURLWithPath:configDirectory()]];
    }
    status("Share a config by sending its .json; drop received ones into that folder and press Refresh.");
    status(configStatus);
    endCard();
    ImGui::SameLine(0, kCardGap);
    beginCard("CONFIGS", ImVec2(layout.right, layout.height));
    float buttons = 30 * 3 + ImGui::GetStyle().ItemSpacing.y * 3 + 8;
    ImGui::BeginChild("##config_list", ImVec2(0, ImGui::GetContentRegionAvail().y - buttons),
                      ImGuiChildFlags_None, ImGuiWindowFlags_NoBackground);
    if (configList.count == 0) status("No configs yet.");
    for (NSString* name in configList) {
        std::string entry = name.UTF8String;
        if (ImGui::Selectable(entry.c_str(), entry == configSelected)) {
            configSelected = entry;
            std::snprintf(configName, sizeof configName, "%s", entry.c_str());
        }
    }
    ImGui::EndChild();
    ImGui::BeginDisabled(configSelected.empty());
    if (actionButton("Load")) {
        if (NSDictionary* state = readState(configPath(configSelected))) {
            applyState(state);
            changed = true;
            configStatus = "Loaded \"" + configSelected + "\"";
        } else {
            configStatus = "Could not read \"" + configSelected + "\"";
        }
    }
    if (actionButton("Delete")) {
        [NSFileManager.defaultManager removeItemAtPath:configPath(configSelected) error:nil];
        configStatus = "Deleted \"" + configSelected + "\"";
        configSelected.clear();
        configList = listConfigs();
    }
    ImGui::EndDisabled();
    if (actionButton("Refresh")) configList = listConfigs();
    endCard();
    return changed;
}

void drawTheme() {
    Columns layout = columns();
    beginCard("ACCENT", ImVec2(layout.left, layout.height));
    ImDrawList* draw = ImGui::GetWindowDrawList();
    float width = ImGui::GetContentRegionAvail().x;
    constexpr int perRow = 4;
    float cell = width / perRow, swatch = 30;
    ImVec2 origin = ImGui::GetCursorScreenPos();
    for (int index = 0; index < (int)std::size(kAccents); ++index) {
        ImVec2 low = origin + ImVec2(cell * (index % perRow), (swatch + 30) * (index / perRow));
        ImGui::SetCursorScreenPos(low);
        ImGui::PushID(index);
        if (ImGui::InvisibleButton("##swatch", ImVec2(cell, swatch + 26)) && accentIndex != index) {
            accentIndex = index;
            applyStyle();
            stateDirty = true;
        }
        bool hovered = ImGui::IsItemHovered();
        ImGui::PopID();
        ImVec2 center = low + ImVec2(cell / 2, swatch / 2);
        ImVec4 color = ImGui::ColorConvertU32ToFloat4(kAccents[index].color);
        if (index == accentIndex) draw->AddCircle(center, swatch / 2 + 4, tone(color), 32, 2);
        draw->AddCircleFilled(center, swatch / 2 - (hovered ? 0 : 1), tone(color));
        ImVec2 size = textSize(kSmallSize, kAccents[index].name);
        textAt(draw, ImVec2(center.x - size.x / 2, low.y + swatch + 8), kSmallSize,
               index == accentIndex ? kText : kMuted, kAccents[index].name);
    }
    int rows = ((int)std::size(kAccents) + perRow - 1) / perRow;
    ImGui::SetCursorScreenPos(origin + ImVec2(0, rows * (swatch + 30)));
    ImGui::Dummy(ImVec2(width, 4));
    status("The accent colors the menu, ESP boxes, arrows and watermark. Team colors still apply with teams.");
    endCard();
    ImGui::SameLine(0, kCardGap);
    ImGui::BeginGroup();
    float top = (layout.height - kCardGap) * 0.5f;
    beginCard("BACKGROUND", ImVec2(layout.right, top));
    if (segmentedIndex("base", "Base", {"Graphite", "OLED", "Slate"}, baseIndex)) {
        applyStyle();
        stateDirty = true;
    }
    endCard();
    ImGui::Dummy(ImVec2(0, kCardGap - ImGui::GetStyle().ItemSpacing.y));
    beginCard("OVERLAY", ImVec2(layout.right, layout.height - top - kCardGap));
    if (switchRow("watermark", "Watermark", showWatermark)) stateDirty = true;
    status("Drawings only appear while Roblox or this menu is the active app.");
    endCard();
    ImGui::EndGroup();
}

void drawSidebar(ImDrawList* draw, ImVec2 origin, ImVec2 size) {
    draw->AddRectFilled(origin, origin + ImVec2(kSidebarWidth, size.y), tone(base().sidebar), kMenuRounding,
                        ImDrawFlags_RoundCornersLeft);
    draw->AddLine(origin + ImVec2(kSidebarWidth, 0), origin + ImVec2(kSidebarWidth, size.y), tone(kLine));
    textAt(draw, origin + ImVec2(22, 22), kLogoSize, kText, "WEIRD");
    textAt(draw, origin + ImVec2(22 + textSize(kLogoSize, "WEIRD").x, 22), kLogoSize, accentColor(), "EXT");
    textAt(draw, origin + ImVec2(22, 22 + kLogoSize + 3), kSmallSize, kMuted, "macOS external");
    float y = 90;
    // Rows shrink to keep every tab above the footer hint.
    float pitch = std::min(40.0f, (size.y - y - 56) / (float)std::size(kTabs));
    for (const TabInfo& info : kTabs) {
        ImGui::PushID(info.label);
        ImVec2 low = origin + ImVec2(12, y), extent(kSidebarWidth - 24, pitch - 4);
        ImGui::SetCursorScreenPos(low);
        if (ImGui::InvisibleButton("##tab", extent)) currentTab = info.tab;
        bool hovered = ImGui::IsItemHovered();
        float t = animate("anim", currentTab == info.tab);
        draw->AddRectFilled(low, low + extent, tone(accentColor(), 0.13f * t), 8);
        if (hovered && t < 0.5f) draw->AddRectFilled(low, low + extent, tone(ImVec4(1, 1, 1, 0.03f)), 8);
        float bar = 18 * t;
        if (bar >= 1) {
            draw->AddRectFilled(low + ImVec2(0, (extent.y - bar) / 2), low + ImVec2(3, (extent.y + bar) / 2),
                                tone(accentColor()), 2);
        }
        textAt(draw, low + ImVec2(16, (extent.y - kFontSize) / 2 - 1), kFontSize,
               mix(hovered ? kText : kMuted, kText, t), info.label);
        ImGui::PopID();
        y += pitch;
    }
    textAt(draw, origin + ImVec2(22, size.y - 46), kSmallSize, kMuted, "Right Shift");
    textAt(draw, origin + ImVec2(22, size.y - 28), kSmallSize, mix(kMuted, base().background, 0.4f), "hides this menu");
}

void drawMenu(ImVec2 bounds) {
    if (!menuOpen) {
        explorerSelected = false;
        return;
    }
    if (explorerRequested) {
        currentTab = Tab::Explorer;
        explorerRequested = false;
    }
    ImGui::SetNextWindowPos(bounds * 0.5f, ImGuiCond_FirstUseEver, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(kMenuWidth, kMenuHeight), ImGuiCond_FirstUseEver);
    // The overlay is the game window's size; a small Roblox window must not clip the menu.
    ImGui::SetNextWindowSizeConstraints(ImVec2(600, 420), ImVec2(std::max(bounds.x - 16, 600.0f),
                                                                 std::max(bounds.y - 16, 420.0f)));
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
    ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, kMenuRounding);
    ImGui::PushStyleColor(ImGuiCol_WindowBg, base().background);
    ImGui::PushStyleColor(ImGuiCol_Border, kLine);
    bool changed = false;
    if (ImGui::Begin("WeirdExt", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse
                                          | ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse)) {
        ImDrawList* draw = ImGui::GetWindowDrawList();
        ImVec2 origin = ImGui::GetWindowPos(), size = ImGui::GetWindowSize();
        ImVec4 accent = accentColor(), clear(accent.x, accent.y, accent.z, 0);
        float middle = origin.x + size.x / 2;
        // Accent hairline across the top edge, fading out toward both corners.
        draw->AddRectFilledMultiColor(ImVec2(origin.x + kMenuRounding, origin.y), ImVec2(middle, origin.y + 2),
                                      tone(clear), tone(accent), tone(accent), tone(clear));
        draw->AddRectFilledMultiColor(ImVec2(middle, origin.y), ImVec2(origin.x + size.x - kMenuRounding, origin.y + 2),
                                      tone(accent), tone(clear), tone(clear), tone(accent));
        drawSidebar(draw, origin, size);

        ImVec2 closeLow = origin + ImVec2(size.x - 40, 16);
        ImGui::SetCursorScreenPos(closeLow);
        bool close = ImGui::InvisibleButton("##close", ImVec2(24, 24));
        ImU32 closeColor = tone(ImGui::IsItemHovered() ? kText : kMuted);
        draw->AddLine(closeLow + ImVec2(7, 7), closeLow + ImVec2(17, 17), closeColor, 1.6f);
        draw->AddLine(closeLow + ImVec2(17, 7), closeLow + ImVec2(7, 17), closeColor, 1.6f);

        const TabInfo& info = *std::find_if(std::begin(kTabs), std::end(kTabs),
                                            [](const TabInfo& entry) { return entry.tab == currentTab; });
        ImVec2 content = origin + ImVec2(kSidebarWidth + 22, 18);
        textAt(draw, content, kTitleSize, kText, info.label);
        textAt(draw, content + ImVec2(0, kTitleSize + 4), kSmallSize, kMuted, info.subtitle);
        ImGui::SetCursorScreenPos(content + ImVec2(0, kTitleSize + kSmallSize + 20));
        ImVec2 area(size.x - kSidebarWidth - 44, size.y - (kTitleSize + kSmallSize + 38) - 22);
        ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(10, 7));
        ImGui::BeginChild("content", area, ImGuiChildFlags_None, ImGuiWindowFlags_NoBackground);
        switch (currentTab) {
            case Tab::Visuals: changed |= drawVisuals(); break;
            case Tab::Player: changed |= drawPlayer(); break;
            case Tab::Aim: changed |= drawAim(); break;
            case Tab::Silent: changed |= drawSilentTab(); break;
            case Tab::Players: drawPlayers(); break;
            case Tab::Keys: drawKeys(ImGui::GetContentRegionAvail().y); break;
            case Tab::Misc: drawMisc(); break;
            case Tab::Theme: drawTheme(); break;
            case Tab::Configs: changed |= drawConfigs(); break;
            case Tab::Explorer: drawExplorer(); break;
        }
        ImGui::EndChild();
        ImGui::PopStyleVar();
        if (currentTab != Tab::Explorer) explorerSelected = false;
        if (close) setMenuOpen(false);
    }
    ImGui::End();
    ImGui::PopStyleColor(2);
    ImGui::PopStyleVar(2);
    if (changed) settingsChanged();
}

void applyStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    ImGui::StyleColorsDark();
    style.WindowRounding = kMenuRounding;
    style.ChildRounding = kCardRounding;
    style.FrameRounding = 6;
    style.GrabRounding = 6;
    style.PopupRounding = 8;
    style.ScrollbarRounding = 6;
    style.ScrollbarSize = 8;
    style.WindowPadding = ImVec2(14, 12);
    style.FramePadding = ImVec2(10, 6);
    style.ItemSpacing = ImVec2(10, 8);
    style.WindowBorderSize = 1;
    style.ChildBorderSize = 1;
    style.FontSizeBase = kFontSize;
    ImVec4 accent = accentColor();
    ImVec4* colors = style.Colors;
    colors[ImGuiCol_Text] = kText;
    colors[ImGuiCol_TextDisabled] = kMuted;
    colors[ImGuiCol_WindowBg] = base().background;
    colors[ImGuiCol_ChildBg] = base().card;
    colors[ImGuiCol_Border] = kLine;
    colors[ImGuiCol_FrameBg] = kTrack;
    colors[ImGuiCol_FrameBgHovered] = ImVec4(1, 1, 1, 0.10f);
    colors[ImGuiCol_FrameBgActive] = ImVec4(1, 1, 1, 0.14f);
    colors[ImGuiCol_Button] = kTrack;
    colors[ImGuiCol_ButtonHovered] = ImVec4(accent.x, accent.y, accent.z, 0.30f);
    colors[ImGuiCol_ButtonActive] = ImVec4(accent.x, accent.y, accent.z, 0.50f);
    colors[ImGuiCol_Header] = ImVec4(accent.x, accent.y, accent.z, 0.20f);
    colors[ImGuiCol_HeaderHovered] = ImVec4(accent.x, accent.y, accent.z, 0.28f);
    colors[ImGuiCol_HeaderActive] = ImVec4(accent.x, accent.y, accent.z, 0.38f);
    colors[ImGuiCol_ScrollbarBg] = ImVec4(0, 0, 0, 0);
    colors[ImGuiCol_ScrollbarGrab] = ImVec4(1, 1, 1, 0.10f);
    colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(1, 1, 1, 0.16f);
    colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(accent.x, accent.y, accent.z, 0.6f);
    colors[ImGuiCol_TextSelectedBg] = ImVec4(accent.x, accent.y, accent.z, 0.35f);
    colors[ImGuiCol_NavCursor] = accent;
    colors[ImGuiCol_Separator] = kLine;
    colors[ImGuiCol_ResizeGrip] = ImVec4(0, 0, 0, 0);
    colors[ImGuiCol_ResizeGripHovered] = ImVec4(accent.x, accent.y, accent.z, 0.4f);
    colors[ImGuiCol_ResizeGripActive] = accent;
}

// ---- Per-tick logic -----------------------------------------------------------------

void trackGameWindow(double now) {
    if (now - lastWindowPoll <= kWindowPollInterval) return;
    lastWindowPoll = now;
    // Persistent overlay: tracks the game window whether or not Roblox is
    // frontmost, so terminal calibration stays visible.
    if (auto game = gameBounds(pid)) {
        lastWindowSeen = now;
        windowAvailable = true;
        CGFloat primaryTop = NSScreen.screens.firstObject.frame.size.height;
        NSRect cocoa = NSMakeRect(game->origin.x, primaryTop - CGRectGetMaxY(*game), game->size.width, game->size.height);
        bool fullscreen = false;
        for (NSScreen* screen in NSScreen.screens) {
            NSRect s = screen.frame;
            fullscreen |= std::abs(cocoa.origin.x - s.origin.x) < 2 && std::abs(cocoa.origin.y - s.origin.y) < 2
                       && std::abs(cocoa.size.width - s.size.width) < 2 && std::abs(cocoa.size.height - s.size.height) < 2;
        }
        double inset = fullscreen ? 0 : topInset;
        NSRect frame = NSMakeRect(cocoa.origin.x + nudgeOffset.width, cocoa.origin.y + nudgeOffset.height,
                                  cocoa.size.width, std::max(1.0, cocoa.size.height - inset));
        // Reconfiguring an unchanged transparent window every poll can disturb its backing surface.
        if (!NSEqualRects(window.frame, frame)) [window setFrame:frame display:NO];
        if (!window.isVisible) [window orderFrontRegardless];
    } else if (now - lastWindowSeen >= kWindowLossGrace) {
        windowAvailable = false;
        if (menuOpen) {
            if (!NSEqualRects(window.frame, fallbackFrame())) [window setFrame:fallbackFrame() display:NO];
        } else {
            [window orderOut:nil];
        }
    }
}

void emitHealth(double now) {
    if (now - lastHealth < 1) return;
    auto [received, rejected] = pendingFrames.counts();
    double span = now - lastHealth;
    id age = presentation.received ? (id)@(std::max(0.0, now - *presentation.received) * 1000) : (id)NSNull.null;
    emit(@{@"type": @"health", @"receive_hz": @((received - previousReceived) / span),
           @"draw_hz": @((drawCount - previousDraws) / span), @"age_ms": age, @"rejected": @(rejected),
           @"window_available": @(windowAvailable),
           @"reason": @((windowAvailable ? presentation.reason(now) : std::string("game window unavailable")).c_str())});
    previousReceived = received;
    previousDraws = drawCount;
    lastHealth = now;
}

void postMouseDelta(int64_t dx, int64_t dy) {
    CGEventRef probe = CGEventCreate(nullptr);
    CGPoint location = CGEventGetLocation(probe);
    CFRelease(probe);
    CGEventRef event = CGEventCreateMouseEvent(nullptr, kCGEventMouseMoved, location, kCGMouseButtonLeft);
    CGEventSetIntegerValueField(event, kCGMouseEventDeltaX, dx);
    CGEventSetIntegerValueField(event, kCGMouseEventDeltaY, dy);
    CGEventPost(kCGHIDEventTap, event);
    CFRelease(event);
}

void tick() {
    double now = uptime();
    bool focused = pid > 0 && NSWorkspace.sharedWorkspace.frontmostApplication.processIdentifier == pid;
    // Draw (and take clicks) only over Roblox or while the menu itself is active.
    presentable = focused || NSApp.isActive;
    window.ignoresMouseEvents = !(menuOpen && presentable);
    bool typing = menuOpen && ImGui::GetIO().WantTextInput;
    bool aimDown = keyDown(aimKey);
    if (aimMode == AimToggle && aimDown && !aimKeyWasDown && focused && !typing && capturing.empty()) {
        aimToggled = !aimToggled;
    }
    aimKeyWasDown = aimDown;
    bool held = aimMode == AimAlways || (aimMode == AimToggle ? aimToggled : aimDown);
    bool inputAvailable = CGPreflightListenEventAccess() || AXIsProcessTrusted();
    bool space = CGEventSourceKeyState(kCGEventSourceStateCombinedSessionState, kVK_Space);
    if (space && !spaceDown && focused && inputAvailable) spacePresses += 1;
    spaceDown = space;
    CGEventFlags flags = CGEventSourceFlagsState(kCGEventSourceStateCombinedSessionState);
    NSMutableArray* keys = [NSMutableArray array];
    for (const auto& [name, code] : {std::pair{@"w", kVK_ANSI_W}, std::pair{@"a", kVK_ANSI_A},
                                     std::pair{@"s", kVK_ANSI_S}, std::pair{@"d", kVK_ANSI_D}}) {
        if (keyDown(code)) [keys addObject:name];
    }
    if (space) [keys addObject:@"space"];
    if (flags & NX_DEVICELSHIFTKEYMASK) [keys addObject:@"shift"];
    // Silent aim maps the cursor's shot ray onto the target.
    id mouse = NSNull.null;
    if (std::optional<ImVec2> cursor = cursorInView()) mouse = @[@(cursor->x), @(cursor->y)];
    emit(@{@"type": @"input", @"focused": @(focused), @"aim_held": @(held), @"mouse": mouse,
           @"space_presses": @(spacePresses), @"available": @(inputAvailable), @"keys": keys});

    // Right Shift toggles the menu from Roblox or the menu itself; typing a
    // capital into the Explorer filter must not close it.
    // Modifiers are not reported by CGEventSourceKeyState; the device flag bits
    // are the only source that separates right Shift from left.
    bool rightShift = flags & NX_DEVICERSHIFTKEYMASK;
    pollHotkeys(focused, typing);
    pollAvatars(now);
    if (stateDirty && now - lastSave >= 1) {
        saveState();
        lastSave = now;
    }
    if (rightShift && !rightShiftDown && !typing && (focused || window.isKeyWindow)) setMenuOpen(!menuOpen);
    rightShiftDown = rightShift;
    static std::optional<std::pair<bool, bool>> lastAccess;
    std::pair<bool, bool> access{CGPreflightListenEventAccess(), AXIsProcessTrusted()};
    if (access != lastAccess) {
        std::cerr << "[overlay] Input Monitoring " << (access.first ? "granted" : "missing")
                  << ", Accessibility " << (access.second ? "granted" : "missing") << std::endl;
        lastAccess = access;
    }

    bool aimEnabled = settings.toggles.at("aim_enabled");
    bool mouseAim = settings.choices["aim_method"] == "mouse";
    bool trusted = aimEnabled && AXIsProcessTrusted();
    std::optional<std::string> aimName;
    if (auto newest = pendingFrames.take()) {
        panel = newest->packet;
        if (panel.aim) aimName = panel.aim->name;
        bool enabled = mouseAim && panel.aimMethod == "mouse" && aimEnabled && panel.aimEnabled && panel.complete;
        // The reader thread can stamp a frame after this tick began; age it against the clock now.
        double age = uptime() - newest->received + panel.readMs / 1000;
        if (auto motion = aimGate.motion(panel.aim, enabled, focused, held, trusted, age)) {
            postMouseDelta(motion->first, motion->second);
        }
        presentation.accept(std::move(*newest));
    } else if (panel.aim) {
        aimName = panel.aim->name;
    }
    if (!focused || !held || !trusted || !aimEnabled || !mouseAim) aimGate.reset();
    std::string method = mouseAim ? "Mouse" : "Camera";
    aimStatus = !aimEnabled ? "Off"
              : (mouseAim && !trusted) ? "Allow mouse control in Accessibility."
              : !focused ? "Focus Roblox"
              : !held ? std::string(aimMode == AimToggle ? "Press " : "Hold ") + keyName(aimKey)
              : panel.readMs > kAimMaxAge * 1000 ? "Paused: memory reads too slow (" + std::to_string((int)panel.readMs) + " ms)"
              : aimName ? method + " aiming at " + *aimName : "No target in radius";

    // Hit sounds: on shoot, every click in Roblox; on damage, an enemy's health dropping
    // within kHitWindow of a click.
    static bool clickDown = false;
    static double lastClick = -1e9;
    static std::map<long long, double> previousHealth;
    bool click = focused && (NSEvent.pressedMouseButtons & 1);
    if (click) lastClick = now;
    if (hitEnabled && hitMode == HitOnShoot && click && !clickDown) playHitSound();
    clickDown = click;
    bool hit = false;
    for (const PlayerRow& player : panel.players) {
        if (!player.health) continue;
        auto previous = previousHealth.find(player.key);
        if (previous != previousHealth.end() && *player.health < previous->second - 1e-4 && !player.teammate
            && now - lastClick < kHitWindow) {
            hit = true;
        }
        previousHealth[player.key] = *player.health;
    }
    if (hitEnabled && hitMode == HitOnDamage && hit) playHitSound();

    trackGameWindow(now);
    CGSize size = metalView.bounds.size;
    if (!CGSizeEqualToSize(size, lastViewport) && size.width > 0 && size.height > 0) {
        emit(@{@"width": @(size.width), @"height": @(size.height)});
        lastViewport = size;
    }
    if (window.isVisible) [metalView draw];
    emitHealth(uptime());
}

void handleLine(const std::string& line) {
    NSData* bytes = [NSData dataWithBytes:line.data() length:line.size()];
    NSDictionary* message = [NSJSONSerialization JSONObjectWithData:bytes options:0 error:nil];
    if (![message isKindOfClass:NSDictionary.class]) {
        pendingFrames.reject();
        return;
    }
    if (NSString* command = message[@"cmd"]; [command isKindOfClass:NSString.class]) {
        auto value = number(message, @"value");
        NSDictionary* incoming = object(message, @"settings");
        auto dx = number(message, @"dx"), dy = number(message, @"dy");
        dispatch_async(dispatch_get_main_queue(), ^{
            if ([command isEqualToString:@"target_pid"] && value && *value >= 0 && *value <= INT32_MAX
                && std::round(*value) == *value) {
                pid = (int)*value;
                lastWindowPoll = 0;
                aimGate.reset();
                panel.aim.reset();
                pendingFrames.take();
                presentation.reset();
            } else if ([command isEqualToString:@"settings_state"] && incoming) {
                settings.apply(incoming);
                // Python's first state is its defaults; saved preferences then win and are echoed back.
                if (!restored) {
                    restored = true;
                    loadState();
                    emit(@{@"type": @"settings", @"settings": settings.snapshot()});
                }
            } else if ([command isEqualToString:@"inset"] && value) {
                topInset = std::clamp(*value, 0.0, 200.0);
            } else if ([command isEqualToString:@"nudge"]) {
                nudgeOffset = CGSizeMake(dx.value_or(0), dy.value_or(0));
            }
        });
        return;
    }
    if ([message[@"type"] isEqual:@"explorer"]) {
        if (NSDictionary* tree = object(message, @"tree")) {
            ExpNode node = decodeNode(tree);
            dispatch_async(dispatch_get_main_queue(), ^{ updateExplorer(node); });
        }
        return;
    }
    if (auto frame = decodeFrame(message)) pendingFrames.publish(std::move(*frame));
    else pendingFrames.reject();
}

}  // namespace

@implementation Overlay

- (void)drawInMTKView:(MTKView*)view {
    id<MTLCommandBuffer> commands = [commandQueue commandBuffer];
    MTLRenderPassDescriptor* pass = view.currentRenderPassDescriptor;
    if (pass == nil) {
        [commands commit];
        return;
    }
    ImGui_ImplMetal_NewFrame(pass);
    ImGui_ImplOSX_NewFrame(view);
    ImGui::NewFrame();
    ImVec2 bounds = ImGui::GetIO().DisplaySize;
    if (presentable) {
        if (windowAvailable) drawESP(ImGui::GetBackgroundDrawList(), bounds, uptime());
        drawMenu(bounds);
    }
    ImGui::Render();
    id<MTLRenderCommandEncoder> encoder = [commands renderCommandEncoderWithDescriptor:pass];
    ImGui_ImplMetal_RenderDrawData(ImGui::GetDrawData(), commands, encoder);
    [encoder endEncoding];
    [commands presentDrawable:view.currentDrawable];
    [commands commit];
    drawCount += 1;
}

- (void)mtkView:(MTKView*)view drawableSizeWillChange:(CGSize)size {
}

- (void)toggleMenu {
    setMenuOpen(!menuOpen);
}

- (void)openExplorer {
    explorerRequested = true;
    setMenuOpen(true);
}

- (void)quit {
    quit();
}

@end

int main(int argc, const char* argv[]) {
    @autoreleasepool {
        pid = argc > 1 ? std::atoi(argv[1]) : 0;
        topInset = argc > 2 ? std::atof(argv[2]) : 28;
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];

        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        metalDevice = device;
        if (device == nil) {
            std::cerr << "[overlay] Metal is unavailable on this Mac\n";
            return 1;
        }
        commandQueue = [device newCommandQueue];
        overlay = [Overlay new];

        NSRect initial = NSMakeRect(100, 100, 1100, 700);
        window = [[OverlayWindow alloc] initWithContentRect:initial styleMask:NSWindowStyleMaskBorderless
                                                    backing:NSBackingStoreBuffered defer:NO];
        window.releasedWhenClosed = NO;
        window.opaque = NO;
        window.backgroundColor = NSColor.clearColor;
        window.hasShadow = NO;
        window.ignoresMouseEvents = YES;
        window.acceptsMouseMovedEvents = YES;
        window.level = NSFloatingWindowLevel;
        window.collectionBehavior = NSWindowCollectionBehaviorCanJoinAllSpaces
                                  | NSWindowCollectionBehaviorFullScreenAuxiliary
                                  | NSWindowCollectionBehaviorIgnoresCycle;

        metalView = [[MTKView alloc] initWithFrame:NSMakeRect(0, 0, initial.size.width, initial.size.height)
                                            device:device];
        metalView.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
        metalView.colorPixelFormat = MTLPixelFormatBGRA8Unorm;
        metalView.clearColor = MTLClearColorMake(0, 0, 0, 0);
        metalView.layer.opaque = NO;
        // The 60 Hz tick drives drawing so logic keeps running while hidden.
        metalView.paused = YES;
        metalView.enableSetNeedsDisplay = NO;
        metalView.delegate = overlay;
        window.contentView = metalView;

        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO();
        // Menu position and size persist next to settings.json.
        static std::string iniPath = std::string(supportDirectory().UTF8String) + "/imgui.ini";
        io.IniFilename = iniPath.c_str();
        // The overlay sits over Roblox; it must never change the game's cursor.
        io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard | ImGuiConfigFlags_NoMouseCursorChange;
        applyStyle();
        if (io.Fonts->AddFontFromFileTTF(kFontPath, kFontSize) == nullptr) {
            std::cerr << "[overlay] could not load " << kFontPath << "\n";
            return 1;
        }
        ImGui_ImplMetal_Init(device);
        ImGui_ImplOSX_Init(metalView);

        statusItem = [NSStatusBar.systemStatusBar statusItemWithLength:NSVariableStatusItemLength];
        statusItem.button.title = @"WE";
        NSMenu* menu = [NSMenu new];
        [menu addItemWithTitle:@"Toggle Menu (Right Shift)" action:@selector(toggleMenu) keyEquivalent:@","].target = overlay;
        [menu addItemWithTitle:@"Explorer…" action:@selector(openExplorer) keyEquivalent:@"e"].target = overlay;
        [menu addItem:NSMenuItem.separatorItem];
        [menu addItemWithTitle:@"Quit WeirdExt" action:@selector(quit) keyEquivalent:@"q"].target = overlay;
        statusItem.menu = menu;

        lastHealth = uptime();
        NSTimer* timer = [NSTimer timerWithTimeInterval:1.0 / kTickHz repeats:YES block:^(NSTimer*) { tick(); }];
        [NSRunLoop.mainRunLoop addTimer:timer forMode:NSRunLoopCommonModes];
        dispatch_async(dispatch_get_main_queue(), ^{
            setMenuOpen(true);
            emit(@{@"type": @"ready"});
        });
        std::thread([] {
            std::string line;
            while (std::getline(std::cin, line)) handleLine(line);
            dispatch_async(dispatch_get_main_queue(), ^{ [NSApp terminate:nil]; });
        }).detach();
        [NSApp run];
    }
    return 0;
}
