import AppKit
import Foundation
import CoreGraphics
import ApplicationServices

struct Marker: Decodable {
    let x: Double
    let y: Double
    let name: String
    let distance: Double
    let w: Double?
    let h: Double?
}

struct ControlCommand: Decodable {
    let cmd: String
    let value: Double?
    let dx: Double?
    let dy: Double?
    let settings: [String: SettingValue]?
}

enum SettingValue: Decodable {
    case toggle(Bool)
    case number(Double)
    case text(String)
    init(from decoder: Decoder) throws {
        let value = try decoder.singleValueContainer()
        if let toggle = try? value.decode(Bool.self) { self = .toggle(toggle) }
        else if let number = try? value.decode(Double.self) { self = .number(number) }
        else { self = .text(try value.decode(String.self)) }
    }
}

struct RenderOptions: Decodable {
    var enabled = true
    var boxes = true
    var names = true
    var distances = true
    var center_marker = true
}

struct DisplayFrame: Decodable {
    let targets: [Marker]
    let status: String
    let roster: Int
    let fov: Double
    let boresight: Boresight?
    var sample_hz: Double? = nil
    var read_ms: Double? = nil
    var complete: Bool? = nil
    var options: RenderOptions? = nil
    var movement_available: Bool? = nil
    var movement_status: String? = nil
    var camera_available: Bool? = nil
    var camera_status: String? = nil
    var aim_enabled: Bool? = nil
    var aim_radius: Double? = nil
    var aim_method: String? = nil
    var noclip_available: Bool? = nil
    var noclip_status: String? = nil
    var toasts: [Toast]? = nil
    var aim: AimStep? = nil
}

struct AimStep: Decodable {
    let dx: Double
    let dy: Double
    let x: Double
    let y: Double
    let name: String
}

struct Toast: Decodable {
    let text: String
    let age: Double
}

struct AimGate {
    private var residual = CGPoint.zero
    mutating func motion(_ step: AimStep?, enabled: Bool, focused: Bool, held: Bool,
                         trusted: Bool, age: TimeInterval) -> (Int64, Int64)? {
        guard enabled, focused, held, trusted, age >= 0, age < 0.05, let step = step,
              step.dx.isFinite, step.dy.isFinite, hypot(step.dx, step.dy) <= 35.001 else {
            residual = .zero
            return nil
        }
        residual.x += step.dx
        residual.y += step.dy
        let dx = Int64(residual.x.rounded()), dy = Int64(residual.y.rounded())
        residual.x -= CGFloat(dx)
        residual.y -= CGFloat(dy)
        return dx == 0 && dy == 0 ? nil : (dx, dy)
    }
}

struct InputRelay {
    private var spaceDown = false
    private(set) var spacePresses = 0

    mutating func sample(focused: Bool, held: Bool, space: Bool, available: Bool) -> [String: Any] {
        if space && !spaceDown && focused && available { spacePresses += 1 }
        spaceDown = space
        return ["type": "input", "focused": focused, "aim_held": held,
                "space_presses": spacePresses, "available": available]
    }
}

struct Boresight: Decodable {
    let x: Double
    let y: Double
}

struct ReceivedFrame {
    let packet: DisplayFrame
    let received: TimeInterval
}

// Bounded mailbox: the main run loop draws only the newest decoded frame.
// A busy UI thread must not replay a growing queue of old player positions.
final class LatestFrameBuffer {
    private let lock = NSLock()
    private var latest: ReceivedFrame?
    private var receivedCount = 0
    private var rejectedCount = 0

    func publish(_ packet: DisplayFrame, received: TimeInterval = ProcessInfo.processInfo.systemUptime) {
        lock.lock()
        defer { lock.unlock() }
        latest = ReceivedFrame(packet: packet, received: received)
        receivedCount += 1
    }

    func take() -> ReceivedFrame? {
        lock.lock()
        defer { lock.unlock() }
        let result = latest
        latest = nil
        return result
    }

    func reject() {
        lock.lock()
        defer { lock.unlock() }
        rejectedCount += 1
    }

    func counts() -> (received: Int, rejected: Int) {
        lock.lock()
        defer { lock.unlock() }
        return (receivedCount, rejectedCount)
    }
}

// Brief invalid camera reads do not erase an otherwise healthy frame. A valid
// empty frame still clears immediately; a stopped reader expires after 250 ms.
final class FramePresentation {
    private(set) var packet: DisplayFrame?
    private(set) var received: TimeInterval?
    private var failure: String?
    let maxAge: TimeInterval = 0.25

    func reset() {
        packet = nil
        received = nil
        failure = nil
    }

    func accept(_ incoming: ReceivedFrame) {
        guard incoming.packet.complete != false else {
            failure = incoming.packet.status
            return
        }
        packet = incoming.packet
        received = incoming.received
        failure = nil
    }

    func isFresh(at now: TimeInterval) -> Bool {
        guard let received = received else { return false }
        return now - received >= 0 && now - received < maxAge
    }

    func reason(at now: TimeInterval) -> String {
        if !isFresh(at: now) { return failure ?? "no fresh valid frame; targets hidden" }
        if let failure = failure { return "brief camera read gap: " + failure }
        return packet?.targets.isEmpty == true ? "valid empty projected frame" : "drawing"
    }
}

// A small diagnostic bitmap alphabet avoids NSFont/NSString/CoreText entirely.
// All rows are five-bit masks. Unknown Unicode scalars render as '?'.
let glyphs: [Character: [UInt8]] = [
    "A": [14,17,17,31,17,17,17], "B": [30,17,17,30,17,17,30],
    "C": [14,17,16,16,16,17,14], "D": [30,17,17,17,17,17,30],
    "E": [31,16,16,30,16,16,31], "F": [31,16,16,30,16,16,16],
    "G": [14,17,16,23,17,17,15], "H": [17,17,17,31,17,17,17],
    "I": [14,4,4,4,4,4,14], "J": [7,2,2,2,2,18,12],
    "K": [17,18,20,24,20,18,17], "L": [16,16,16,16,16,16,31],
    "M": [17,27,21,21,17,17,17], "N": [17,25,21,19,17,17,17],
    "O": [14,17,17,17,17,17,14], "P": [30,17,17,30,16,16,16],
    "Q": [14,17,17,17,21,18,13], "R": [30,17,17,30,20,18,17],
    "S": [15,16,16,14,1,1,30], "T": [31,4,4,4,4,4,4],
    "U": [17,17,17,17,17,17,14], "V": [17,17,17,17,17,10,4],
    "W": [17,17,17,21,21,21,10], "X": [17,17,10,4,10,17,17],
    "Y": [17,17,10,4,4,4,4], "Z": [31,1,2,4,8,16,31],
    "0": [14,17,19,21,25,17,14], "1": [4,12,4,4,4,4,14],
    "2": [14,17,1,2,4,8,31], "3": [30,1,1,14,1,1,30],
    "4": [2,6,10,18,31,2,2], "5": [31,16,16,30,1,1,30],
    "6": [14,16,16,30,17,17,14], "7": [31,1,2,4,8,8,8],
    "8": [14,17,17,14,17,17,14], "9": [14,17,17,15,1,1,14],
    " ": [0,0,0,0,0,0,0], "?": [14,17,1,2,4,0,4],
    ".": [0,0,0,0,0,12,12], ",": [0,0,0,0,4,4,8],
    ":": [0,4,4,0,4,4,0], ";": [0,4,4,0,4,4,8],
    "-": [0,0,0,31,0,0,0], "_": [0,0,0,0,0,0,31],
    "/": [1,2,2,4,8,8,16], "|": [4,4,4,4,4,4,4],
    "+": [0,4,4,31,4,4,0], "=": [0,0,31,0,31,0,0],
    "(": [2,4,8,8,8,4,2], ")": [8,4,2,2,2,4,8],
    "[": [14,8,8,8,8,8,14], "]": [14,2,2,2,2,2,14],
    "!": [4,4,4,4,4,0,4]
]

func bitmapText(_ text: String, context: CGContext, x: CGFloat, y: CGFloat,
                scale: CGFloat, color: CGColor, centered: Bool = false) {
    let characters = Array(text.uppercased())
    let start = centered ? x - CGFloat(characters.count * 6) * scale / 2 : x
    context.saveGState()
    context.setShouldAntialias(false)
    context.setFillColor(color)
    for (index, character) in characters.enumerated() {
        let rows = glyphs[character] ?? glyphs["?"]!
        for (row, bits) in rows.enumerated() {
            for column in 0..<5 where bits & (1 << (4 - column)) != 0 {
                context.fill(CGRect(x: start + CGFloat(index * 6 + column) * scale,
                                    y: y + CGFloat(row) * scale, width: scale, height: scale))
            }
        }
    }
    context.restoreGState()
}

func renderOverlay(_ context: CGContext, bounds: CGRect, packet: DisplayFrame?, fresh: Bool) {
    context.clear(bounds)
    let options = packet?.options ?? RenderOptions()
    guard options.enabled else { return }
    let cyan = CGColor(red: 0.2, green: 0.9, blue: 1, alpha: 1)
    let white = CGColor(gray: 1, alpha: 1)
    if options.center_marker {
    context.setStrokeColor(CGColor(gray: 1, alpha: 0.6))
    context.move(to: CGPoint(x: bounds.midX - 5, y: bounds.midY))
    context.addLine(to: CGPoint(x: bounds.midX + 5, y: bounds.midY))
    context.move(to: CGPoint(x: bounds.midX, y: bounds.midY - 5))
    context.addLine(to: CGPoint(x: bounds.midX, y: bounds.midY + 5))
    context.strokePath()
    }
    guard fresh, let frame = packet else { return }
    if frame.aim_enabled == true, let radius = frame.aim_radius, radius.isFinite,
       radius >= 20, radius <= 400 {
        context.setStrokeColor(CGColor(gray: 1, alpha: 0.28))
        context.setLineWidth(1)
        context.strokeEllipse(in: CGRect(x: bounds.midX - radius, y: bounds.midY - radius,
                                         width: radius * 2, height: radius * 2))
    }
    // Overlay-center reference only. This does not validate camera pose/FOV,
    // and a custom game's crosshair need not be at the render-area center.
    if options.center_marker, let bore = frame.boresight, bore.x.isFinite, bore.y.isFinite,
       bore.x >= -0.05, bore.x <= 1.05, bore.y >= -0.05, bore.y <= 1.05 {
        let bx = CGFloat(bore.x) * bounds.width
        let by = CGFloat(bore.y) * bounds.height
        context.setFillColor(CGColor(red: 1, green: 1, blue: 0.3, alpha: 1))
        let diamond = NSBezierPath()
        diamond.move(to: NSPoint(x: bx, y: by - 7))
        diamond.line(to: NSPoint(x: bx + 7, y: by))
        diamond.line(to: NSPoint(x: bx, y: by + 7))
        diamond.line(to: NSPoint(x: bx - 7, y: by))
        diamond.close()
        diamond.fill()
    }
    for marker in frame.targets {
        guard marker.x.isFinite, marker.y.isFinite, marker.distance.isFinite,
              marker.distance >= 0, marker.distance < 1e9,
              marker.x >= 0, marker.x <= 1, marker.y >= 0, marker.y <= 1 else { continue }
        let x = CGFloat(marker.x) * bounds.width
        let y = CGFloat(marker.y) * bounds.height
        let label = [options.names ? String(marker.name.prefix(40)) : nil,
                     options.distances ? "\(Int(marker.distance)) STUDS" : nil].compactMap { $0 }.joined(separator: " ")
        let labelWidth = CGFloat(label.uppercased().count * 6) * 1.4
        if let w = marker.w, let h = marker.h, w.isFinite, h.isFinite, w > 0.001, h > 0.001 {
            let rect = CGRect(x: x - CGFloat(w) * bounds.width / 2,
                              y: y - CGFloat(h) * bounds.height / 2,
                              width: CGFloat(w) * bounds.width,
                              height: CGFloat(h) * bounds.height)
            if options.boxes {
                context.setStrokeColor(cyan)
                context.setLineWidth(2)
                context.stroke(rect)
            }
            let labelY = rect.minY - 20
            guard !label.isEmpty else { continue }
            context.setFillColor(CGColor(gray: 0, alpha: 0.8))
            context.fill(CGRect(x: x - labelWidth / 2 - 3, y: labelY, width: labelWidth + 6, height: 14))
            bitmapText(label, context: context, x: x, y: labelY + 2, scale: 1.4, color: white, centered: true)
        } else {
            if options.boxes {
                context.setFillColor(cyan)
                context.fillEllipse(in: CGRect(x: x - 3, y: y - 3, width: 6, height: 6))
            }
            guard !label.isEmpty else { continue }
            context.setFillColor(CGColor(gray: 0, alpha: 0.8))
            context.fill(CGRect(x: x - labelWidth / 2 - 3, y: y - 20, width: labelWidth + 6, height: 14))
            bitmapText(label, context: context, x: x, y: y - 18, scale: 1.4, color: white, centered: true)
        }
    }
    // Join/leave feed: top-right pills, fading over four seconds.
    for toast in frame.toasts ?? [] where toast.age >= 0 && toast.age < 4 && !toast.text.isEmpty {
        let alpha = max(0, min(1, 1 - toast.age / 4))
        let text = String(toast.text.prefix(44)).uppercased()
        let width = CGFloat(text.count * 6) * 1.2 + 14
        let y = bounds.height - 34
        context.setFillColor(CGColor(gray: 0.04, alpha: 0.85 * alpha))
        context.fill(CGRect(x: bounds.width - width - 14, y: y, width: width, height: 20))
        bitmapText(text, context: context, x: bounds.width - width - 7, y: y + 5,
                   scale: 1.2, color: CGColor(red: 0.2, green: 0.9, blue: 1, alpha: alpha))
    }
}

final class OverlayView: NSView {
    let presentation = FramePresentation()
    var drawCount = 0
    override var isFlipped: Bool { true }
    override var isOpaque: Bool { false }

    override func draw(_ dirtyRect: NSRect) {
        guard let context = NSGraphicsContext.current?.cgContext else { return }
        drawCount += 1
        let fresh = presentation.isFresh(at: ProcessInfo.processInfo.systemUptime)
        renderOverlay(context, bounds: bounds, packet: presentation.packet, fresh: fresh)
    }
}

final class PassiveWindow: NSWindow {
    override var canBecomeKey: Bool { false }
    override var canBecomeMain: Bool { false }
}

final class SettingsPanel: NSObject, NSWindowDelegate {
    let panel: NSPanel
    private var checks: [String: NSButton] = [:]
    private var sliders: [String: NSSlider] = [:]
    private var values: [String: NSTextField] = [:]
    private let movementStatus = NSTextField(wrappingLabelWithString: "Connecting…")
    private let cameraStatus = NSTextField(wrappingLabelWithString: "Default FOV")
    private let aimStatus = NSTextField(wrappingLabelWithString: "Off")
    private var aimMethod: NSSegmentedControl?

    var aimMethodLabel: String { aimMethod?.selectedSegment == 1 ? "Camera" : "Mouse" }
    private let pages = NSTabView()
    private var tabButtons: [NSButton] = []
    private let emit: ([String: Any]) -> Void
    private var menuItem: NSStatusItem?

    private let explorerDelegate: ExplorerPanel?

    init(installMenu: Bool = true, emit: @escaping ([String: Any]) -> Void,
         explorerDelegate: ExplorerPanel? = nil) {
        self.explorerDelegate = explorerDelegate
        self.emit = emit
        panel = NSPanel(contentRect: NSRect(x: 100, y: 100, width: 368, height: 500),
                        styleMask: [.titled, .closable], backing: .buffered, defer: false)
        super.init()
        panel.title = "WeirdExt"
        panel.appearance = NSAppearance(named: .darkAqua)
        panel.level = .floating
        panel.hidesOnDeactivate = false
        panel.isReleasedWhenClosed = false
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.delegate = self
        let root = NSStackView()
        root.orientation = .vertical
        root.alignment = .leading
        root.spacing = 16
        root.translatesAutoresizingMaskIntoConstraints = false
        let content = panel.contentView!
        content.addSubview(root)
        NSLayoutConstraint.activate([root.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 20),
                                     root.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -20),
                                     root.topAnchor.constraint(equalTo: content.topAnchor, constant: 18),
                                     root.bottomAnchor.constraint(lessThanOrEqualTo: content.bottomAnchor, constant: -16)])
        func label(_ text: String, size: CGFloat, weight: NSFont.Weight) -> NSTextField {
            let label = NSTextField(labelWithString: text)
            label.font = NSFont.systemFont(ofSize: size, weight: weight)
            return label
        }
        let tabs = NSStackView()
        tabs.orientation = .horizontal
        tabs.distribution = .fillEqually
        for (index, title) in ["Visuals", "Player", "Aim"].enumerated() {
            let button = NSButton(title: title, target: self, action: #selector(switchTab(_:)))
            button.isBordered = false
            button.bezelStyle = .inline
            button.tag = index
            tabs.addArrangedSubview(button)
            tabButtons.append(button)
        }
        root.addArrangedSubview(tabs)
        tabs.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true
        pages.tabViewType = .noTabsNoBorder
        root.addArrangedSubview(pages)
        pages.widthAnchor.constraint(equalTo: root.widthAnchor).isActive = true
        pages.heightAnchor.constraint(equalToConstant: 386).isActive = true
        func page(_ title: String) -> NSStackView {
            let item = NSTabViewItem(identifier: title)
            item.label = title
            let container = NSView()
            let stack = NSStackView()
            stack.orientation = .vertical
            stack.alignment = .leading
            stack.spacing = 10
            stack.translatesAutoresizingMaskIntoConstraints = false
            container.addSubview(stack)
            NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                                         stack.trailingAnchor.constraint(equalTo: container.trailingAnchor),
                                         stack.topAnchor.constraint(equalTo: container.topAnchor, constant: 4)])
            item.view = container
            pages.addTabViewItem(item)
            return stack
        }
        var stack = page("Visuals")
        func check(_ key: String, _ title: String, _ enabled: Bool) -> NSButton {
            let button = NSButton(checkboxWithTitle: title, target: self, action: #selector(changed(_:)))
            button.state = enabled ? .on : .off
            checks[key] = button
            return button
        }
        func row(_ controls: [NSView]) {
            let row = NSStackView(views: controls)
            row.orientation = .horizontal
            row.spacing = 18
            stack.addArrangedSubview(row)
        }
        func slider(_ key: String, _ title: String, _ initial: Double, _ low: Double, _ high: Double) {
            let caption = label(title, size: 12, weight: .regular)
            let value = label("", size: 12, weight: .medium)
            value.font = NSFont.monospacedDigitSystemFont(ofSize: 12, weight: .regular)
            value.alignment = .right
            let heading = NSStackView(views: [caption, NSView(), value])
            heading.orientation = .horizontal
            stack.addArrangedSubview(heading)
            heading.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
            let control = NSSlider(value: initial, minValue: low, maxValue: high, target: self, action: #selector(changed(_:)))
            control.isContinuous = true
            sliders[key] = control
            values[key] = value
            stack.addArrangedSubview(control)
            control.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
        }
        func status(_ field: NSTextField) {
            field.font = NSFont.systemFont(ofSize: 11)
            field.textColor = .secondaryLabelColor
            field.maximumNumberOfLines = 3
            stack.addArrangedSubview(field)
            field.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
            field.heightAnchor.constraint(equalToConstant: 42).isActive = true
        }
        row([check("esp_enabled", "ESP", true)])
        row([check("boxes", "Boxes", true), check("names", "Names", true), check("distances", "Distance", true)])
        row([check("center_marker", "Center mark", true), check("show_local", "Show me", false)])
        slider("box_height", "Height", 5.4, 1, 20)
        slider("box_ratio", "Width", 0.6, 0.2, 2)
        slider("fps", "Update rate", 60, 1, 60)
        row([check("fov_enabled", "Change FOV", false)])
        slider("fov", "FOV", 70, 30, 120)
        status(cameraStatus)
        stack = page("Player")
        row([check("walk_speed_enabled", "Change Speed", false)])
        slider("walk_speed", "Speed", 16, 0, 150)
        row([check("jump_power_enabled", "Change Jump", false)])
        slider("jump_power", "Jump", 50, 0, 200)
        row([check("noclip", "Noclip", false), check("infinite_jump", "Infinite Jump", false)])
        let inputAccess = NSButton(title: "Allow keyboard input…", target: self, action: #selector(requestInputAccess))
        inputAccess.bezelStyle = .rounded
        stack.addArrangedSubview(inputAccess)
        status(movementStatus)
        stack = page("Aim")
        row([check("aim_enabled", "Aimbot", false)])
        let methodLabel = label("Method", size: 12, weight: .regular)
        let method = NSSegmentedControl(labels: ["Mouse", "Camera"], trackingMode: .selectOne,
                                        target: self, action: #selector(changed(_:)))
        method.selectedSegment = 0
        aimMethod = method
        let methodRow = NSStackView(views: [methodLabel, NSView(), method])
        methodRow.orientation = .horizontal
        stack.addArrangedSubview(methodRow)
        methodRow.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
        slider("aim_radius", "Radius", 140, 20, 400)
        slider("aim_smoothing", "Smoothness", 6, 1, 20)
        let help = label("Hold right mouse in Roblox. Targets the body.", size: 11, weight: .regular)
        help.textColor = .secondaryLabelColor
        stack.addArrangedSubview(help)
        let access = NSButton(title: "Allow mouse control…", target: self, action: #selector(requestAimAccess))
        access.bezelStyle = .rounded
        stack.addArrangedSubview(access)
        status(aimStatus)
        pages.selectTabViewItem(at: 0)
        updateTabs(0)
        let footer = label("Close to hide. Reopen from WE in the menu bar.", size: 10, weight: .regular)
        footer.textColor = .tertiaryLabelColor
        root.addArrangedSubview(footer)
        refreshValues()
        setMovement(available: false, status: movementStatus.stringValue)
        setCamera(available: false, status: cameraStatus.stringValue)
        content.layoutSubtreeIfNeeded()
        panel.center()
        if installMenu {
            let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
            item.button?.title = "WE"
            let menu = NSMenu()
            let settings = menu.addItem(withTitle: "Settings…", action: #selector(openSettings), keyEquivalent: ",")
            settings.target = self
            let explorer = menu.addItem(withTitle: "Explorer…", action: #selector(openExplorer), keyEquivalent: "e")
            explorer.target = self
            menu.addItem(.separator())
            let quit = menu.addItem(withTitle: "Quit WeirdExt", action: #selector(quit), keyEquivalent: "q")
            quit.target = self
            item.menu = menu
            menuItem = item
        }
    }

    func snapshot() -> [String: Any] {
        var result: [String: Any] = checks.mapValues { $0.state == .on }
        for (key, slider) in sliders { result[key] = slider.doubleValue }
        result["aim_method"] = aimMethod?.selectedSegment == 1 ? "camera" : "mouse"
        return result
    }

    private func refreshValues() {
        for (key, slider) in sliders {
            values[key]?.stringValue = String(format: key == "box_ratio" || key == "box_height" ? "%.2f" : "%.0f", slider.doubleValue)
        }
    }

    func apply(_ settings: [String: SettingValue]) {
        for (key, value) in settings {
            switch value {
            case .toggle(let enabled): checks[key]?.state = enabled ? .on : .off
            case .text(let method) where key == "aim_method":
                aimMethod?.selectedSegment = method == "camera" ? 1 : 0
            case .number(let number):
                if number.isFinite, let slider = sliders[key] {
                    slider.doubleValue = min(max(number, slider.minValue), slider.maxValue)
                }
            default: break
            }
        }
        refreshValues()
    }

    func setMovement(available: Bool, status: String) {
        for key in ["walk_speed_enabled", "jump_power_enabled"] {
            checks[key]?.isEnabled = available
        }
        if movementStatus.stringValue != status { movementStatus.stringValue = status }
    }

    func setCamera(available: Bool, status: String) {
        checks["fov_enabled"]?.isEnabled = available
        if cameraStatus.stringValue != status { cameraStatus.stringValue = status }
    }

    func setPhysics(available: Bool, status: String) {
        for key in ["noclip", "infinite_jump"] { checks[key]?.isEnabled = available }
        if movementStatus.stringValue != status { movementStatus.stringValue = status }
    }

    var aimEnabled: Bool { checks["aim_enabled"]?.state == .on }
    var mouseAim: Bool { aimMethod?.selectedSegment != 1 }

    func setAimStatus(_ status: String) {
        if aimStatus.stringValue != status { aimStatus.stringValue = status }
    }

    private func updateTabs(_ selected: Int) {
        for (index, button) in tabButtons.enumerated() {
            button.attributedTitle = NSAttributedString(string: button.title, attributes: [
                .font: NSFont.systemFont(ofSize: 13, weight: index == selected ? .semibold : .regular),
                .foregroundColor: index == selected ? NSColor.labelColor : NSColor.secondaryLabelColor,
                .underlineStyle: index == selected ? NSUnderlineStyle.single.rawValue : 0
            ])
        }
    }

    @objc func switchTab(_ sender: NSButton) {
        pages.selectTabViewItem(at: sender.tag)
        updateTabs(sender.tag)
    }

    @objc func requestAimAccess() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true] as CFDictionary
        setAimStatus(AXIsProcessTrustedWithOptions(options) ? "Hold right mouse" : "Enable WeirdExt in Accessibility.")
    }

    @objc func requestInputAccess() {
        let allowed = CGRequestListenEventAccess()
        movementStatus.stringValue = allowed ? "Keyboard input allowed" : "Enable WeirdExt in Input Monitoring, then restart."
    }

    @objc func changed(_ sender: Any?) {
        for key in ["fps", "fov", "walk_speed", "jump_power", "aim_radius", "aim_smoothing"] {
            if let slider = sliders[key] { slider.doubleValue = slider.doubleValue.rounded() }
        }
        refreshValues()
        emit(["type": "settings", "settings": snapshot()])
    }

    @objc func openSettings() {
        panel.makeKeyAndOrderFront(nil)
        NSApplication.shared.activate(ignoringOtherApps: true)
    }

    @objc func openExplorer() {
        explorerDelegate?.open()
    }

    @objc func quit() {
        for key in ["walk_speed_enabled", "jump_power_enabled", "noclip", "infinite_jump",
                    "fov_enabled", "aim_enabled"] {
            checks[key]?.state = .off
        }
        changed(nil)
        emit(["type": "quit"])
        panel.orderOut(nil)
    }

    func windowShouldClose(_ sender: NSWindow) -> Bool {
        sender.orderOut(nil)
        return false
    }
}

final class ExpNode: Decodable {
    let name: String
    let cls: String?
    let truncated: Bool?
    var kids: [ExpNode]?

    init(name: String, cls: String? = nil, truncated: Bool? = nil, kids: [ExpNode]? = nil) {
        self.name = name
        self.cls = cls
        self.truncated = truncated
        self.kids = kids
    }
}

// Decodes {"type":"explorer","tree":{...}} from the reader.
struct ExplorerUpdate: Decodable {
    let type: String
    let tree: ExpNode?
}

func matches(_ node: ExpNode, _ query: String) -> Bool {
    if query.isEmpty { return true }
    if node.name.localizedCaseInsensitiveContains(query)
        || (node.cls ?? "").localizedCaseInsensitiveContains(query) { return true }
    return (node.kids ?? []).contains { matches($0, query) }
}

func filterTree(_ nodes: [ExpNode], _ query: String) -> [ExpNode] {
    guard !query.isEmpty else { return nodes }
    var result: [ExpNode] = []
    for node in nodes {
        let kids = filterTree(node.kids ?? [], query)
        if node.name.localizedCaseInsensitiveContains(query)
            || (node.cls ?? "").localizedCaseInsensitiveContains(query) || !kids.isEmpty {
            let copy = ExpNode(name: node.name, cls: node.cls, truncated: node.truncated)
            copy.kids = kids
            result.append(copy)
        }
    }
    return result
}

final class ExplorerPanel: NSObject, NSOutlineViewDataSource, NSOutlineViewDelegate {
    let panel: NSPanel
    private let outline = NSOutlineView()
    private let scroll = NSScrollView()
    private let search = NSSearchField()
    private let status = NSTextField(labelWithString: "Idle")
    private var roots: [ExpNode] = []
    private var query = ""
    private var snapshotCount = 0
    let refresh: () -> Void

    init(refresh: @escaping () -> Void) {
        self.refresh = refresh
        panel = NSPanel(contentRect: NSRect(x: 120, y: 120, width: 460, height: 620),
                        styleMask: [.titled, .closable, .resizable, .utilityWindow],
                        backing: .buffered, defer: false)
        super.init()
        panel.title = "WeirdExt Explorer"
        panel.appearance = NSAppearance(named: .darkAqua)
        panel.isReleasedWhenClosed = false
        panel.hidesOnDeactivate = false
        let content = panel.contentView!
        search.placeholderString = "Filter by name or class"
        search.target = self
        search.action = #selector(searchChanged)
        status.font = NSFont.systemFont(ofSize: 10)
        status.textColor = .secondaryLabelColor
        let column = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("name"))
        column.title = "Name"
        column.width = 280
        let classColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("cls"))
        classColumn.title = "Class"
        classColumn.width = 120
        outline.addTableColumn(column)
        outline.addTableColumn(classColumn)
        outline.dataSource = self
        outline.delegate = self
        outline.indentationPerLevel = 12
        outline.usesAlternatingRowBackgroundColors = true
        outline.rowSizeStyle = .small
        scroll.documentView = outline
        scroll.hasVerticalScroller = true
        scroll.translatesAutoresizingMaskIntoConstraints = false
        search.translatesAutoresizingMaskIntoConstraints = false
        status.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(search)
        content.addSubview(scroll)
        content.addSubview(status)
        let refreshButton = NSButton(title: "Refresh", target: self, action: #selector(refreshClicked))
        refreshButton.bezelStyle = .rounded
        refreshButton.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(refreshButton)
        NSLayoutConstraint.activate([
            search.topAnchor.constraint(equalTo: content.topAnchor, constant: 12),
            search.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 14),
            search.trailingAnchor.constraint(equalTo: refreshButton.leadingAnchor, constant: -8),
            refreshButton.centerYAnchor.constraint(equalTo: search.centerYAnchor),
            refreshButton.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -14),
            scroll.topAnchor.constraint(equalTo: search.bottomAnchor, constant: 10),
            scroll.leadingAnchor.constraint(equalTo: content.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: content.trailingAnchor),
            status.topAnchor.constraint(equalTo: scroll.bottomAnchor, constant: 6),
            status.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 14),
            status.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -10),
        ])
    }

    func open() {
        panel.makeKeyAndOrderFront(nil)
        NSApplication.shared.activate(ignoringOtherApps: true)
        refresh()
    }

    @objc func refreshClicked() { refresh() }

    @objc func searchChanged() {
        query = search.stringValue
        expandedKeys = nil
        reload(expandAll: true)
    }

    func update(_ tree: ExpNode?) {
        snapshotCount += 1
        status.stringValue = "Snapshot \(snapshotCount) · updated"
        captureExpanded()
        roots = tree.map { [$0] } ?? []
        reload()
    }

    // Expansion survives Refresh: key by name|class. nil means "first load".
    private var expandedKeys: Set<String>?

    private func key(of node: ExpNode?) -> String {
        guard let node else { return "" }
        return node.name + "|" + (node.cls ?? "?")
    }

    private func captureExpanded() {
        var keys = Set<String>()
        for row in 0..<outline.numberOfRows {
            let item = outline.item(atRow: row)
            if outline.isItemExpanded(item), let node = item as? ExpNode {
                keys.insert(key(of: node))
            }
        }
        expandedKeys = keys
    }

    private func reload(expandAll: Bool = false) {
        outline.reloadData()
        for row in 0..<outline.numberOfRows {
            let item = outline.item(atRow: row)
            guard let node = item as? ExpNode else { continue }
            if expandAll || expandedKeys?.contains(key(of: node)) == true {
                outline.expandItem(item)
            }
        }
        if expandedKeys == nil, outline.numberOfRows > 0 {
            outline.expandItem(outline.item(atRow: 0))
        }
    }

    func outlineView(_ outlineView: NSOutlineView, numberOfChildrenOfItem item: Any?) -> Int {
        let nodes = item == nil ? filterTree(roots, query) : (item as? ExpNode)?.kids ?? []
        return nodes.count
    }

    func outlineView(_ outlineView: NSOutlineView, isItemExpandable item: Any) -> Bool {
        !((item as? ExpNode)?.kids ?? []).isEmpty
    }

    func outlineView(_ outlineView: NSOutlineView, child index: Int, ofItem item: Any?) -> Any {
        let nodes = item == nil ? filterTree(roots, query) : (item as? ExpNode)?.kids ?? []
        return nodes[index]
    }

    func outlineView(_ outlineView: NSOutlineView, objectValueFor tableColumn: NSTableColumn?,
                     byItem item: Any?) -> Any? {
        guard let node = item as? ExpNode else { return nil }
        let suffix = node.truncated == true ? " …" : ""
        if tableColumn?.identifier.rawValue == "cls" { return (node.cls ?? "?") }
        return node.name + suffix
    }
}

func emitViewport(_ width: CGFloat, _ height: CGFloat) {
    guard let encoded = try? JSONSerialization.data(withJSONObject: [
        "width": Double(width), "height": Double(height)
    ]) else { return }
    FileHandle.standardOutput.write(encoded + Data([10]))
}

func gameBounds(_ pid: Int) -> CGRect? {
    guard let entries = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements],
                                                  kCGNullWindowID) as? [[String: Any]] else { return nil }
    var best: CGRect?
    for entry in entries {
        guard (entry[kCGWindowOwnerPID as String] as? NSNumber)?.intValue == pid,
              (entry[kCGWindowLayer as String] as? NSNumber)?.intValue == 0,
              let box = entry[kCGWindowBounds as String] as? [String: Any],
              let x = box["X"] as? NSNumber, let y = box["Y"] as? NSNumber,
              let width = box["Width"] as? NSNumber, let height = box["Height"] as? NSNumber
        else { continue }
        let rect = CGRect(x: x.doubleValue, y: y.doubleValue,
                          width: width.doubleValue, height: height.doubleValue)
        if rect.width < 200 || rect.height < 150 { continue }
        if best == nil || rect.width * rect.height > best!.width * best!.height { best = rect }
    }
    return best
}

let arguments = CommandLine.arguments
var pid = Int(arguments.dropFirst().first ?? "0") ?? 0
var topInset = Double(arguments.last ?? "28") ?? 28
var nudgeOffset = CGSize.zero
let application = NSApplication.shared
application.setActivationPolicy(.accessory)
let emitControl: ([String: Any]) -> Void = { event in
    if let encoded = try? JSONSerialization.data(withJSONObject: event) {
        FileHandle.standardOutput.write(encoded + Data([10]))
    }
}
let explorerPanel = ExplorerPanel { emitControl(["type": "explorer_refresh"]) }
let settingsPanel = SettingsPanel(installMenu: true, emit: { event in
    emitControl(event)
}, explorerDelegate: explorerPanel)
let initial = NSRect(x: 100, y: 100, width: 1100, height: 700)
let window = PassiveWindow(contentRect: initial, styleMask: [.borderless], backing: .buffered, defer: false)
let view = OverlayView(frame: NSRect(origin: .zero, size: initial.size))
view.autoresizingMask = [.width, .height]
window.contentView = view
window.isReleasedWhenClosed = false
window.isOpaque = false
window.backgroundColor = .clear
window.hasShadow = false
window.ignoresMouseEvents = true
window.level = .floating
window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .ignoresCycle]

var lastViewport = NSSize.zero
var lastWindowPoll: TimeInterval = 0
var lastWindowSeen: TimeInterval = 0
var lastHealth: TimeInterval = ProcessInfo.processInfo.systemUptime
var previousReceived = 0
var previousDraws = 0
var windowAvailable = false
var aimGate = AimGate()
var aimName: String?
var inputRelay = InputRelay()
let pendingFrames = LatestFrameBuffer()
let timer = Timer(timeInterval: 1.0 / 60.0, repeats: true) { _ in
    let now = ProcessInfo.processInfo.systemUptime
    let focused = Int(NSWorkspace.shared.frontmostApplication?.processIdentifier ?? -1) == pid
        && !settingsPanel.panel.isKeyWindow
    let held = NSEvent.pressedMouseButtons & 2 != 0
    let inputAvailable = CGPreflightListenEventAccess() || AXIsProcessTrusted()
    let space = CGEventSource.keyState(.combinedSessionState, key: 49)
    emitControl(inputRelay.sample(focused: focused, held: held, space: space, available: inputAvailable))
    let trusted = settingsPanel.aimEnabled && AXIsProcessTrusted()
    if let newest = pendingFrames.take() {
        view.presentation.accept(newest)
        settingsPanel.setMovement(available: newest.packet.movement_available == true,
                                  status: newest.packet.movement_status ?? "Not connected")
        settingsPanel.setCamera(available: newest.packet.camera_available == true,
                                status: newest.packet.camera_status ?? "Not connected")
        settingsPanel.setPhysics(available: newest.packet.noclip_available == true,
                                 status: newest.packet.noclip_status ?? "Not connected")
        aimName = newest.packet.aim?.name
        let enabled = settingsPanel.mouseAim && newest.packet.aim_method == "mouse"
            && settingsPanel.aimEnabled && newest.packet.aim_enabled == true && newest.packet.complete != false
        if let motion = aimGate.motion(newest.packet.aim, enabled: enabled, focused: focused,
                                       held: held, trusted: trusted,
                                       age: now - newest.received + max(0, newest.packet.read_ms ?? 0) / 1000),
           let location = CGEvent(source: nil)?.location,
           let event = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved,
                               mouseCursorPosition: location, mouseButton: .left) {
            event.setIntegerValueField(.mouseEventDeltaX, value: motion.0)
            event.setIntegerValueField(.mouseEventDeltaY, value: motion.1)
            event.post(tap: .cghidEventTap)
        }
    }
    if !focused || !held || !trusted || !settingsPanel.aimEnabled || !settingsPanel.mouseAim {
        _ = aimGate.motion(nil, enabled: false, focused: false, held: false, trusted: false, age: 0)
    }
    let method = settingsPanel.aimMethodLabel
    settingsPanel.setAimStatus(!settingsPanel.aimEnabled ? "Off" :
        (settingsPanel.mouseAim && !trusted) ? "Allow mouse control in Accessibility." : !focused ? "Focus Roblox" :
        !held ? "Hold right mouse" : aimName.map { method + " aiming at " + $0 } ?? "No target in radius")
    if now - lastWindowPoll > 0.25 {
        lastWindowPoll = now
        // Persistent overlay: tracks the game window whether or not Roblox
        // is the frontmost app, so calibration from the terminal is visible.
        if let game = gameBounds(pid) {
            lastWindowSeen = now
            windowAvailable = true
            let primaryTop = NSScreen.screens.first?.frame.maxY ?? 0
            let cocoa = NSRect(x: game.minX, y: primaryTop - game.maxY,
                               width: game.width, height: game.height)
            let fullscreen = NSScreen.screens.contains { screen in
                abs(cocoa.minX - screen.frame.minX) < 2 && abs(cocoa.minY - screen.frame.minY) < 2 &&
                abs(cocoa.width - screen.frame.width) < 2 && abs(cocoa.height - screen.frame.height) < 2
            }
            let inset = fullscreen ? 0 : topInset
            let frame = NSRect(x: cocoa.minX + nudgeOffset.width,
                               y: cocoa.minY + nudgeOffset.height,
                               width: cocoa.width,
                               height: max(1, cocoa.height - inset))
            // Reconfiguring/reordering an unchanged transparent window on
            // every poll is unnecessary and can disturb its backing surface.
            if window.frame != frame { window.setFrame(frame, display: false) }
            if !window.isVisible { window.orderFrontRegardless() }
        } else if now - lastWindowSeen >= 0.5 {
            windowAvailable = false
            window.orderOut(nil)
        }
    }
    let size = view.bounds.size
    if size != lastViewport && size.width > 0 && size.height > 0 {
        emitViewport(size.width, size.height)
        lastViewport = size
    }
    view.needsDisplay = true
    if now - lastHealth >= 1 {
        let counts = pendingFrames.counts()
        let span = now - lastHealth
        let age: Any
        if let received = view.presentation.received { age = max(0, now - received) * 1000 }
        else { age = NSNull() }
        let health: [String: Any] = [
            "type": "health", "receive_hz": Double(counts.received - previousReceived) / span,
            "draw_hz": Double(view.drawCount - previousDraws) / span, "age_ms": age,
            "rejected": counts.rejected, "window_available": windowAvailable,
            "reason": windowAvailable ? view.presentation.reason(at: now) : "game window unavailable"
        ]
        if let encoded = try? JSONSerialization.data(withJSONObject: health) {
            FileHandle.standardOutput.write(encoded + Data([10]))
        }
        previousReceived = counts.received
        previousDraws = view.drawCount
        lastHealth = now
    }
}
RunLoop.main.add(timer, forMode: .common)
DispatchQueue.main.async {
    settingsPanel.openSettings()
    FileHandle.standardOutput.write(Data("{\"type\":\"ready\"}\n".utf8))
}

DispatchQueue.global(qos: .userInitiated).async {
    while let line = readLine() {
        guard let bytes = line.data(using: .utf8) else { continue }
        if let control = try? JSONDecoder().decode(ControlCommand.self, from: bytes) {
            if control.cmd == "target_pid", let value = control.value,
               value.isFinite, value >= 0, value <= Double(Int32.max), value.rounded() == value {
                DispatchQueue.main.async {
                    pid = Int(value)
                    lastWindowPoll = 0
                    aimGate = AimGate()
                    aimName = nil
                    _ = pendingFrames.take()
                    view.presentation.reset()
                }
            }
            if control.cmd == "settings_state", let settings = control.settings {
                DispatchQueue.main.async { settingsPanel.apply(settings) }
            }
            if control.cmd == "inset", let value = control.value, value.isFinite {
                DispatchQueue.main.async { topInset = min(max(value, 0), 200) }
            }
            if control.cmd == "nudge" {
                let dx = control.dx ?? 0
                let dy = control.dy ?? 0
                if dx.isFinite && dy.isFinite {
                    DispatchQueue.main.async { nudgeOffset = CGSize(width: dx, height: dy) }
                }
            }
            continue
        }
        if let update = try? JSONDecoder().decode(ExplorerUpdate.self, from: bytes),
           update.type == "explorer", let tree = update.tree {
            DispatchQueue.main.async { explorerPanel.update(tree) }
            continue
        }
        guard let decoded = try? JSONDecoder().decode(DisplayFrame.self, from: bytes) else {
            pendingFrames.reject()
            continue
        }
        pendingFrames.publish(decoded)
    }
    DispatchQueue.main.async { application.terminate(nil) }
}
application.run()
