// Dump what a macOS keyboard layout produces for every virtual keycode 0..127
// under a set of modifier states, by asking the OS itself (UCKeyTranslate).
// usage: swift dumplayout.swift <input-source-id> [json]
import Carbon
import Foundation

let args = CommandLine.arguments
guard args.count >= 2 else { fputs("usage: dumplayout <source-id> [json]\n", stderr); exit(2) }
let wantID = args[1]
let asJSON = args.count > 2 && (args[2] == "json" || args[2] == "full")

// find the source by id (not the current one — we want to inspect layouts that are not active)
let filter = [kTISPropertyInputSourceID as String: wantID] as CFDictionary
guard let list = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource],
      let src = list.first else {
    fputs("no input source \(wantID)\n", stderr); exit(1)
}
guard let dataPtr = TISGetInputSourceProperty(src, kTISPropertyUnicodeKeyLayoutData) else {
    fputs("\(wantID) has no uchr data (an IME, not a keylayout?)\n", stderr); exit(1)
}
let data = Unmanaged<CFData>.fromOpaque(dataPtr).takeUnretainedValue() as Data

// modifier states as UCKeyTranslate wants them: (EventModifiers >> 8) & 0xFF
let fullMode = args.count > 2 && args[2] == "full"
var states: [(String, UInt32)] = []
if fullMode {
    // every combination of the five modifier bits a .keylayout can select on;
    // names use the keylayout's own vocabulary so the generator can emit them verbatim
    let bits: [(String, Int)] = [("anyShift", shiftKey), ("caps", alphaLock), ("anyOption", optionKey),
                                 ("command", cmdKey), ("anyControl", controlKey)]
    for mask in 0..<32 {
        var name: [String] = []; var mods = 0
        for (i, b) in bits.enumerated() where mask & (1 << i) != 0 { name.append(b.0); mods |= b.1 }
        states.append((name.isEmpty ? "" : name.joined(separator: " "), UInt32(mods >> 8)))
    }
} else {
    states = [
        ("none",   0),
        ("shift",  UInt32(shiftKey >> 8)),
        ("caps",   UInt32(alphaLock >> 8)),
        ("opt",    UInt32(optionKey >> 8)),
        ("optsh",  UInt32((optionKey | shiftKey) >> 8)),
        ("cmd",    UInt32(cmdKey >> 8)),
        ("ctrl",   UInt32(controlKey >> 8)),
    ]
}

func translate(_ code: UInt16, _ mods: UInt32) -> String {
    var dead: UInt32 = 0
    var chars = [UniChar](repeating: 0, count: 8)
    var len = 0
    let st = data.withUnsafeBytes { raw -> OSStatus in
        let p = raw.baseAddress!.assumingMemoryBound(to: UCKeyboardLayout.self)
        return UCKeyTranslate(p, code, UInt16(kUCKeyActionDown), mods,
                              UInt32(LMGetKbdType()), OptionBits(kUCKeyTranslateNoDeadKeysBit),
                              &dead, 8, &len, &chars)
    }
    if st != noErr { return "<err>" }
    if dead != 0 { return "<dead>" }
    return String(utf16CodeUnits: chars, count: len)
}

var table: [[String: Any]] = []
for code in 0..<128 {
    var row: [String: Any] = ["code": code]
    for (name, m) in states { row[name] = translate(UInt16(code), m) }
    table.append(row)
}

if asJSON {
    let j = try! JSONSerialization.data(withJSONObject: table, options: [.sortedKeys])
    print(String(data: j, encoding: .utf8)!)
} else {
    print("code  " + states.map { $0.0.padding(toLength: 6, withPad: " ", startingAt: 0) }.joined())
    for row in table {
        func show(_ k: String) -> String {
            let s = row[k] as! String
            let v = s.isEmpty ? "·" : s.unicodeScalars.map { $0.value < 0x20 ? String(format: "^%02X", $0.value) : String($0) }.joined()
            return v.padding(toLength: 6, withPad: " ", startingAt: 0)
        }
        print(String(format: "%3d   ", row["code"] as! Int) + states.map { show($0.0) }.joined())
    }
}
