import AppKit

@main
final class AppDelegate: NSObject, NSApplicationDelegate {
    private let statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
    private var timer: Timer?
    private var server: Process?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Handoffer", action: nil, keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Open dashboard", action: #selector(openDashboard), keyEquivalent: "o"))
        menu.addItem(NSMenuItem(title: "Refresh", action: #selector(refresh), keyEquivalent: "r"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit Handoffer", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        statusItem.menu = menu
        statusItem.button?.title = "Handoff —"
        startServer()
        refresh()
        timer = Timer.scheduledTimer(timeInterval: 60, target: self, selector: #selector(refresh), userInfo: nil, repeats: true)
    }

    private func startServer() {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: NSHomeDirectory() + "/.config/handoffer/serve")
        try? process.run()
        server = process
    }

    @objc private func openDashboard() {
        NSWorkspace.shared.open(URL(string: "http://127.0.0.1:8765")!)
    }

    @objc private func refresh() {
        let url = URL(string: "http://127.0.0.1:8765/api/status")!
        URLSession.shared.dataTask(with: url) { [weak self] data, _, _ in
            guard let self, let data,
                  let payload = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let agents = payload["agents"] as? [[String: Any]] else { return }
            let values = agents.compactMap { agent -> Int? in
                guard let fiveHour = agent["five_hour"] as? [String: Any],
                      let value = fiveHour["remaining_percent"] as? Double else { return nil }
                return Int(value.rounded())
            }
            DispatchQueue.main.async { self.statusItem.button?.title = values.isEmpty ? "Handoff —" : "Handoff \\(values.min() ?? 0)%" }
        }.resume()
    }
}
