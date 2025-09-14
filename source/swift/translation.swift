import Foundation
import Translate

let inputURL = URL(fileURLWithPath: "/path/to/input.txt")
guard let inputText = try? String(contentsOf: inputURL) else {
    print("Failed to read input file.")
    exit(1)
}

let codesURL = URL(fileURLWithPath: "/path/to/target_languages.txt")
guard let codesText = try? String(contentsOf: codesURL) else {
    print("Failed to read language codes file.")
    exit(1)
}
let targetLanguageCodes = codesText.split(separator: "\n").map { String($0) }

let sourceLanguage = Locale(identifier: "en")
let translator = Translator()

Task {
    for code in targetLanguageCodes {
        let targetLanguage = Locale(identifier: code)
        let request = TranslationRequest(
            sourceLanguage: sourceLanguage,
            targetLanguage: targetLanguage,
            text: inputText
        )
        do {
            let result = try await translator.translate(request: request)
            let outputPath = "/path/to/output_\(code).txt"
            try result.translatedText.write(toFile: outputPath, atomically: true, encoding: .utf8)
            print("Translated to \(code): \(outputPath)")
        } catch {
            print("Translation to \(code) failed: \(error)")
        }
    }
    exit(0)
}
RunLoop.main.run()