// Tiny TIS CLI: list / enable / disable / select input sources by id.
// Exists so the RussianWinPlus cutover and rollback are commands, not a tour of
// System Settings. usage:
//   tis list                  every keyboard layout TIS knows: id  enabled?  selected?
//   tis enable  <source-id>   add it to the input menu
//   tis disable <source-id>   remove it from the input menu. DOES NOT FAIL on the selected
//                             source — macOS silently selects another one. Always `select`
//                             the one you want active BEFORE disabling anything.
//   tis select  <source-id>   make it the active layout now
import Carbon
import Foundation

func source(_ id: String) -> TISInputSource? {
    let filter = [kTISPropertyInputSourceID as String: id] as CFDictionary
    let list = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource]
    return list?.first
}
func flag(_ s: TISInputSource, _ key: CFString) -> Bool {
    guard let p = TISGetInputSourceProperty(s, key) else { return false }
    return CFBooleanGetValue(Unmanaged<CFBoolean>.fromOpaque(p).takeUnretainedValue())
}
func str(_ s: TISInputSource, _ key: CFString) -> String {
    guard let p = TISGetInputSourceProperty(s, key) else { return "" }
    return Unmanaged<CFString>.fromOpaque(p).takeUnretainedValue() as String
}

let a = CommandLine.arguments
guard a.count >= 2 else { fputs("usage: tis list | enable ID | disable ID | select ID\n", stderr); exit(2) }

switch a[1] {
case "list":
    let filter = [kTISPropertyInputSourceType as String: kTISTypeKeyboardLayout as String] as CFDictionary
    let all = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource] ?? []
    for s in all {
        let id = str(s, kTISPropertyInputSourceID)
        if !(id.contains("Russian") || id.contains("ABC") || id.hasPrefix("org.bekh")) { continue }
        print("\(flag(s, kTISPropertyInputSourceIsEnabled) ? "on " : "off") \(flag(s, kTISPropertyInputSourceIsSelected) ? "*" : " ") \(id)")
    }
case "enable", "disable", "select":
    guard a.count == 3, let s = source(a[2]) else { fputs("no input source \(a.count == 3 ? a[2] : "?")\n", stderr); exit(1) }
    let st: OSStatus
    switch a[1] {
    case "enable":  st = TISEnableInputSource(s)
    case "disable": st = TISDisableInputSource(s)
    default:        st = TISSelectInputSource(s)
    }
    if st != noErr { fputs("\(a[1]) \(a[2]) failed: OSStatus \(st)\n", stderr); exit(1) }
    print("\(a[1]) \(a[2]): ok")
default:
    fputs("unknown verb \(a[1])\n", stderr); exit(2)
}
