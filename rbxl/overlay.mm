// WeirdExt overlay helper: Dear ImGui on Metal, driven by JSON lines on stdin.
// Python owns all memory access. This process draws, relays input state and
// posts bounded mouse deltas; it never receives a task port.

#define IMGUI_DEFINE_MATH_OPERATORS
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#import <Carbon/Carbon.h>
#import <IOKit/hidsystem/IOLLEvent.h>
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
constexpr double kAimMaxAge = 0.05;
constexpr double kWindowPollInterval = 0.25;
constexpr double kWindowLossGrace = 0.5;
constexpr double kToastLifetime = 4.0;
constexpr int kNameLimit = 40;
constexpr int kToastLimit = 44;
constexpr float kFontSize = 14.0f;
constexpr float kLabelSize = 13.0f;
constexpr ImU32 kAccent = IM_COL32(51, 230, 255, 255);
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
};

struct Offscreen {
    double angle = 0, distance = 0;
    std::string name;
    int team = 0;
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

struct DisplayFrame {
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
    frame.complete = packet[@"complete"] == nil || flag(packet, @"complete");
    frame.readMs = std::max(0.0, number(packet, @"read_ms").value_or(0));
    for (NSDictionary* entry in targets) {
        if (![entry isKindOfClass:NSDictionary.class]) return std::nullopt;
        auto x = number(entry, @"x"), y = number(entry, @"y"), distance = number(entry, @"distance");
        if (!x || !y || !distance) return std::nullopt;
        Marker marker{*x, *y, *distance, number(entry, @"w"), number(entry, @"h"),
                      text(entry, @"name", kNameLimit), {}, number(entry, @"health"),
                      (int)number(entry, @"team").value_or(0)};
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
                                       (int)number(entry, @"team").value_or(0)});
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
    {"aim_radius", 20, 400, true}, {"aim_smoothing", 1, 20, true}, {"fly_speed", 5, 300, true},
};

const std::map<std::string, std::vector<std::string>> kChoices{
    {"aim_method", {"mouse", "camera"}}, {"aim_part", {"head", "torso", "closest"}},
    {"aim_priority", {"crosshair", "distance"}}};

// Features that write game memory: never restored from disk, always start off.
const char* const kWriteFeatures[] = {"walk_speed_enabled", "jump_power_enabled", "noclip",
                                      "infinite_jump", "fov_enabled", "aim_enabled", "fly"};

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
        {"fly", false}};
    std::map<std::string, double> numbers{
        {"box_height", 5.4}, {"box_ratio", 0.6}, {"fps", 60}, {"fov", 70}, {"walk_speed", 16},
        {"jump_power", 50}, {"aim_radius", 140}, {"aim_smoothing", 6}, {"fly_speed", 50}};
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
                              {"walk_speed_enabled", "Speed"}};

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
    {kVK_ANSI_Backslash, "\\"}, {kVK_Tab, "Tab"}, {kVK_CapsLock, "Caps Lock"}};

const char* keyName(int code) {
    for (const auto& [key, name] : kKeyNames) {
        if (key == code) return name;
    }
    return "?";
}

bool keyDown(int code) { return CGEventSourceKeyState(kCGEventSourceStateCombinedSessionState, (CGKeyCode)code); }

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
void saveState() {
    NSMutableDictionary* bound = [NSMutableDictionary dictionary];
    for (const auto& [feature, code] : binds) bound[@(feature.c_str())] = @(code);
    NSData* data = [NSJSONSerialization dataWithJSONObject:@{@"settings": settings.snapshot(false), @"binds": bound}
                                                   options:NSJSONWritingPrettyPrinted error:nil];
    NSError* error = nil;
    if (![data writeToFile:statePath() options:NSDataWritingAtomic error:&error]) {
        std::cerr << "[overlay] settings not saved: " << error.localizedDescription.UTF8String << std::endl;
    }
    stateDirty = false;
}

void loadState() {
    NSData* data = [NSData dataWithContentsOfFile:statePath()];
    if (data == nil) return;
    NSDictionary* state = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
    if (![state isKindOfClass:NSDictionary.class]) {
        std::cerr << "[overlay] ignoring unreadable " << statePath().UTF8String << std::endl;
        return;
    }
    if (NSDictionary* saved = object(state, @"settings")) settings.apply(saved, false);
    if (NSDictionary* saved = object(state, @"binds")) {
        for (const Bindable& feature : kBindable) {
            if (auto code = number(saved, @(feature.key)); code && *code >= 0 && *code < 128) binds[feature.key] = (int)*code;
        }
    }
}

void settingsChanged() {
    emit(@{@"type": @"settings", @"settings": settings.snapshot()});
    stateDirty = true;
}

void pollHotkeys(bool focused, bool typing) {
    if (!capturing.empty()) {
        if (keyDown(kVK_Escape)) {
            binds.erase(capturing);
            capturing.clear();
            stateDirty = true;
            return;
        }
        for (const auto& [code, name] : kKeyNames) {
            bool held = std::find(capturingHeld.begin(), capturingHeld.end(), code) != capturingHeld.end();
            if (keyDown(code) && !held) {
                binds[capturing] = code;
                bindDown[capturing] = true;  // the capturing press must not also toggle
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

const ImU32 kTeamColors[] = {IM_COL32(255, 99, 99, 255), IM_COL32(110, 160, 255, 255), IM_COL32(120, 230, 120, 255),
                             IM_COL32(255, 205, 80, 255), IM_COL32(200, 130, 255, 255), IM_COL32(255, 150, 60, 255)};

ImU32 teamColor(int team) { return team > 0 ? kTeamColors[(team - 1) % std::size(kTeamColors)] : kAccent; }

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
    ImU32 color = teamColor(target.team);
    draw->AddTriangleFilled(tip + direction, base + normal * 8, base - normal * 8, kShadow);
    draw->AddTriangleFilled(tip, base + normal * 7, base - normal * 7, color);
    if (distances) drawLabel(draw, base - direction * 10, false, std::to_string((int)target.distance), color);
}

void drawESP(ImDrawList* draw, ImVec2 bounds, double now) {
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
        ImU32 color = teamColor(marker.team);
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
        draw->AddText(ImGui::GetFont(), kLabelSize, pos, (kAccent & ~IM_COL32_A_MASK) | ((ImU32)alpha << IM_COL32_A_SHIFT),
                      toast.text.c_str());
        y += size.y + 14;
    }
}

// ---- Menu -------------------------------------------------------------------------

bool toggle(const char* key, const char* label) {
    return ImGui::Checkbox(label, &settings.toggles.at(key));
}

bool slider(const char* key, const char* label) {
    for (const Slider& entry : kSliders) {
        if (std::string(key) != entry.key) continue;
        double& value = settings.numbers.at(key);
        ImGui::SetNextItemWidth(-FLT_MIN);
        bool changed = ImGui::SliderScalar(label, ImGuiDataType_Double, &value, &entry.low, &entry.high,
                                           entry.integral ? (std::string(label).substr(2) + " %.0f").c_str()
                                                          : (std::string(label).substr(2) + " %.2f").c_str(),
                                           ImGuiSliderFlags_AlwaysClamp);
        if (changed && entry.integral) value = std::round(value);
        return changed;
    }
    throw std::logic_error(std::string("unknown slider ") + key);
}

// One row of radio buttons for a settings choice; labels follow kChoices order.
bool choice(const char* key, const char* label, std::initializer_list<const char*> labels) {
    const auto& values = kChoices.at(key);
    bool changed = false;
    ImGui::PushID(key);
    ImGui::TextUnformatted(label);
    size_t index = 0;
    for (const char* option : labels) {
        ImGui::SameLine();
        if (ImGui::RadioButton(option, settings.choices[key] == values.at(index))) {
            settings.choices[key] = values.at(index);
            changed = true;
        }
        index += 1;
    }
    ImGui::PopID();
    return changed;
}

void status(const std::string& message) {
    if (message.empty()) return;
    ImGui::PushStyleColor(ImGuiCol_Text, ImGui::GetStyleColorVec4(ImGuiCol_TextDisabled));
    ImGui::TextWrapped("%s", message.c_str());
    ImGui::PopStyleColor();
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
    ImGui::TextDisabled("%s", node.cls.c_str());
    if (open && !node.kids.empty()) {
        for (size_t i = 0; i < node.kids.size(); ++i) drawExplorerNode(node.kids[i], (int)i, depth + 1);
        ImGui::TreePop();
    }
    ImGui::PopID();
}

void copyRow(const char* label, const std::string& value) {
    ImGui::PushID(label);
    ImGui::TextDisabled("%s", label);
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
    ImGui::SetNextItemWidth(-ImGui::CalcTextSize("Refresh").x - ImGui::GetStyle().FramePadding.x * 2
                            - ImGui::GetStyle().ItemSpacing.x);
    if (ImGui::InputTextWithHint("##filter", "Filter by name or class", explorerQuery, sizeof explorerQuery)) {
        explorerVisible = filterTree(explorerRoots, explorerQuery);
        explorerExpandAll = explorerQuery[0] != 0;
    }
    ImGui::SameLine();
    if (ImGui::Button("Refresh")) requestExplorer();
    status(explorerStatus);
    float details = explorerChosen ? ImGui::GetTextLineHeightWithSpacing() * 5 + 8 : 0;
    if (ImGui::BeginChild("tree", ImVec2(0, -details), ImGuiChildFlags_Borders)) {
        for (size_t i = 0; i < explorerVisible.size(); ++i) drawExplorerNode(explorerVisible[i], (int)i, 0);
    }
    ImGui::EndChild();
    if (explorerChosen) {
        copyRow("Name", explorerChosen->name);
        copyRow("Class", explorerChosen->cls);
        copyRow("Address", explorerChosen->address);
        copyRow("Parent", explorerChosen->parent);
        copyRow("Children", std::to_string(explorerChosen->kids.size()) + (explorerChosen->truncated ? "+" : ""));
    }
    explorerExpandAll = false;
}

void drawKeys() {
    status("Click a feature, then press a key. Esc clears. Keys toggle while Roblox is focused.");
    for (const Bindable& feature : kBindable) {
        ImGui::PushID(feature.key);
        ImGui::TextUnformatted(feature.label);
        ImGui::SameLine(140);
        bool waiting = capturing == feature.key;
        std::string label = waiting ? "Press a key…" : binds.count(feature.key) ? keyName(binds[feature.key]) : "None";
        if (ImGui::Button(label.c_str(), ImVec2(140, 0)) && !waiting) {
            capturing = feature.key;
            capturingHeld.clear();
            for (const auto& [code, name] : kKeyNames) {
                if (keyDown(code)) capturingHeld.push_back(code);
            }
        }
        ImGui::PopID();
    }
    ImGui::Separator();
    status("Right Shift always toggles this menu.");
}

void drawMenu(ImVec2 bounds) {
    if (!menuOpen) return;
    ImGui::SetNextWindowPos(bounds * 0.5f, ImGuiCond_FirstUseEver, ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(440, 580), ImGuiCond_FirstUseEver);
    // The overlay is the game window's size; a small Roblox window must not clip the menu's title and tabs.
    ImGui::SetNextWindowSizeConstraints(ImVec2(320, 240), ImVec2(std::max(bounds.x - 16, 320.0f), std::max(bounds.y - 16, 240.0f)));
    bool open = true;
    bool changed = false;
    if (ImGui::Begin("WeirdExt", &open, ImGuiWindowFlags_NoCollapse)) {
        ImGuiTabItemFlags explorerFlags = explorerRequested ? ImGuiTabItemFlags_SetSelected : 0;
        explorerRequested = false;
        bool explorerVisibleNow = false;
        if (ImGui::BeginTabBar("tabs")) {
            if (ImGui::BeginTabItem("Visuals")) {
                changed |= toggle("esp_enabled", "ESP");
                changed |= toggle("boxes", "Boxes");
                ImGui::SameLine();
                changed |= toggle("names", "Names");
                ImGui::SameLine();
                changed |= toggle("distances", "Distance");
                changed |= toggle("esp_skeleton", "Skeleton");
                ImGui::SameLine();
                changed |= toggle("esp_tracers", "Tracers");
                ImGui::SameLine();
                changed |= toggle("esp_offscreen", "Off-screen arrows");
                changed |= toggle("esp_health", "Health bars");
                ImGui::SameLine();
                changed |= toggle("team_check", "Hide teammates");
                changed |= toggle("center_marker", "Center mark");
                ImGui::SameLine();
                changed |= toggle("show_local", "Show me");
                status("Health and team need their offsets in the profile (probe_offsets.py).");
                changed |= slider("box_height", "##Fallback height");
                changed |= slider("box_ratio", "##Fallback width");
                changed |= slider("fps", "##Update rate");
                ImGui::Separator();
                ImGui::BeginDisabled(!panel.cameraAvailable);
                changed |= toggle("fov_enabled", "Change FOV");
                ImGui::EndDisabled();
                changed |= slider("fov", "##FOV");
                status(panel.cameraStatus);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Player")) {
                ImGui::BeginDisabled(!panel.movementAvailable);
                changed |= toggle("walk_speed_enabled", "Change Speed");
                ImGui::EndDisabled();
                changed |= slider("walk_speed", "##Speed");
                ImGui::BeginDisabled(!panel.movementAvailable);
                changed |= toggle("jump_power_enabled", "Change Jump");
                ImGui::EndDisabled();
                changed |= slider("jump_power", "##Jump");
                status(panel.movementStatus);
                ImGui::Separator();
                ImGui::BeginDisabled(!panel.noclipAvailable);
                changed |= toggle("noclip", "Noclip");
                ImGui::SameLine();
                changed |= toggle("infinite_jump", "Infinite Jump");
                ImGui::SameLine();
                changed |= toggle("fly", "Fly");
                ImGui::EndDisabled();
                changed |= slider("fly_speed", "##Fly speed");
                status("Fly: WASD follows the camera, Space rises, Left Shift sinks.");
                status(panel.noclipStatus);
                if (ImGui::Button("Allow keyboard input…")) {
                    keyboardNote = CGRequestListenEventAccess() ? "Keyboard input allowed"
                                                                : "Enable WeirdExt in Input Monitoring, then restart.";
                }
                status(keyboardNote);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Aim")) {
                changed |= toggle("aim_enabled", "Aimbot");
                ImGui::SameLine();
                changed |= toggle("aim_sticky", "Sticky target");
                changed |= choice("aim_method", "Method  ", {"Mouse", "Camera"});
                changed |= choice("aim_part", "Part    ", {"Head", "Torso", "Closest"});
                changed |= choice("aim_priority", "Priority", {"Crosshair", "Distance"});
                changed |= slider("aim_radius", "##Radius");
                changed |= slider("aim_smoothing", "##Smoothness");
                status("Hold right mouse in Roblox. Hide teammates (Visuals) also skips them here.");
                if (ImGui::Button("Allow mouse control…")) {
                    NSDictionary* options = @{(__bridge NSString*)kAXTrustedCheckOptionPrompt: @YES};
                    AXIsProcessTrustedWithOptions((__bridge CFDictionaryRef)options);
                }
                status(aimStatus);
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Keys")) {
                drawKeys();
                ImGui::EndTabItem();
            }
            if (ImGui::BeginTabItem("Explorer", nullptr, explorerFlags)) {
                explorerVisibleNow = true;
                drawExplorer();
                ImGui::EndTabItem();
            }
            ImGui::EndTabBar();
        }
        if (!explorerVisibleNow) explorerSelected = false;
    }
    ImGui::End();
    if (changed) settingsChanged();
    if (!open) setMenuOpen(false);
}

void applyStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    ImGui::StyleColorsDark();
    style.WindowRounding = 8;
    style.ChildRounding = 6;
    style.FrameRounding = 5;
    style.GrabRounding = 5;
    style.TabRounding = 5;
    style.WindowPadding = ImVec2(14, 12);
    style.FramePadding = ImVec2(8, 5);
    style.ItemSpacing = ImVec2(10, 8);
    style.WindowBorderSize = 1;
    style.FontSizeBase = kFontSize;
    ImVec4 accent = ImGui::ColorConvertU32ToFloat4(kAccent);
    ImVec4* colors = style.Colors;
    colors[ImGuiCol_WindowBg] = ImVec4(0.07f, 0.08f, 0.09f, 1.0f);
    colors[ImGuiCol_ChildBg] = ImVec4(0.05f, 0.06f, 0.07f, 1.0f);
    colors[ImGuiCol_Border] = ImVec4(1, 1, 1, 0.08f);
    colors[ImGuiCol_TitleBg] = colors[ImGuiCol_TitleBgActive] = ImVec4(0.09f, 0.10f, 0.12f, 1.0f);
    colors[ImGuiCol_FrameBg] = ImVec4(1, 1, 1, 0.06f);
    colors[ImGuiCol_FrameBgHovered] = ImVec4(1, 1, 1, 0.10f);
    colors[ImGuiCol_FrameBgActive] = ImVec4(1, 1, 1, 0.14f);
    colors[ImGuiCol_CheckMark] = colors[ImGuiCol_SliderGrabActive] = accent;
    colors[ImGuiCol_SliderGrab] = ImVec4(accent.x, accent.y, accent.z, 0.75f);
    colors[ImGuiCol_Button] = ImVec4(1, 1, 1, 0.07f);
    colors[ImGuiCol_ButtonHovered] = ImVec4(accent.x, accent.y, accent.z, 0.30f);
    colors[ImGuiCol_ButtonActive] = ImVec4(accent.x, accent.y, accent.z, 0.45f);
    colors[ImGuiCol_Header] = ImVec4(accent.x, accent.y, accent.z, 0.18f);
    colors[ImGuiCol_HeaderHovered] = ImVec4(accent.x, accent.y, accent.z, 0.28f);
    colors[ImGuiCol_HeaderActive] = ImVec4(accent.x, accent.y, accent.z, 0.38f);
    colors[ImGuiCol_Tab] = ImVec4(1, 1, 1, 0.04f);
    colors[ImGuiCol_TabHovered] = ImVec4(accent.x, accent.y, accent.z, 0.30f);
    colors[ImGuiCol_TabSelected] = ImVec4(accent.x, accent.y, accent.z, 0.22f);
    colors[ImGuiCol_TabSelectedOverline] = accent;
    colors[ImGuiCol_Separator] = colors[ImGuiCol_Border];
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
    bool held = (NSEvent.pressedMouseButtons & 2) != 0;
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
    emit(@{@"type": @"input", @"focused": @(focused), @"aim_held": @(held),
           @"space_presses": @(spacePresses), @"available": @(inputAvailable), @"keys": keys});

    // Right Shift toggles the menu from Roblox or the menu itself; typing a
    // capital into the Explorer filter must not close it.
    // Modifiers are not reported by CGEventSourceKeyState; the device flag bits
    // are the only source that separates right Shift from left.
    bool rightShift = flags & NX_DEVICERSHIFTKEYMASK;
    bool typing = menuOpen && ImGui::GetIO().WantTextInput;
    pollHotkeys(focused, typing);
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
        double age = now - newest->received + panel.readMs / 1000;
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
              : !held ? "Hold right mouse"
              : aimName ? method + " aiming at " + *aimName : "No target in radius";

    trackGameWindow(now);
    CGSize size = metalView.bounds.size;
    if (!CGSizeEqualToSize(size, lastViewport) && size.width > 0 && size.height > 0) {
        emit(@{@"width": @(size.width), @"height": @(size.height)});
        lastViewport = size;
    }
    if (window.isVisible) [metalView draw];
    emitHealth(now);
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
    if (windowAvailable) drawESP(ImGui::GetBackgroundDrawList(), bounds, uptime());
    drawMenu(bounds);
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
