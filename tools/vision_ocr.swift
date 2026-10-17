// macOS Vision OCR for a page image: prints one line per recognised text box as
//   y<TAB>x<TAB>confidence<TAB>text        (y from the TOP of the image, 0-1000 scale)
// Usage: swiftc -O tools/vision_ocr.swift -o /tmp/vision_ocr && /tmp/vision_ocr page.jpg [lang,lang]
// CANDIDATE FINDER ONLY. Handwriting is read poorly; a miss proves nothing ("an absent
// mark is not a record"), a hit is only a place to look by eye.
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 2, let img = NSImage(contentsOfFile: args[1]),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot read image\n".data(using: .utf8)!); exit(1)
}
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = (args.count >= 3 ? args[2] : "hr,la,de,en").split(separator: ",").map(String.init)
req.minimumTextHeight = 0.004
try VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for o in (req.results ?? []) {
    guard let c = o.topCandidates(1).first else { continue }
    let b = o.boundingBox
    print(String(format: "%d\t%d\t%.2f\t%@", Int((1 - b.maxY) * 1000), Int(b.minX * 1000), c.confidence, c.string))
}
