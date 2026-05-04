import SwiftUI

struct ContentView: View {
    @State private var sourceText = ""
    @State private var selectedCharacter = "tabby_cat"
    @State private var isLoading = false
    @State private var resultVideoURL: String?

    let characters: [(id: String, name: String, emoji: String)] = [
        ("tabby_cat", "狸花猫", "🐱"),
        ("brown_bear", "棕熊", "🐻"),
        ("little_fox", "小狐狸", "🦊"),
        ("panda", "熊猫", "🐼"),
        ("rabbit", "兔子", "🐰"),
        ("shiba_inu", "柴犬", "🐶"),
        ("owl", "猫头鹰", "🦉"),
        ("penguin", "企鹅", "🐧"),
    ]

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 8) {
                        Text("🔥 单身动画")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        Text("AI 动漫视频生成器")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top, 20)

                    // Input
                    VStack(alignment: .leading, spacing: 8) {
                        Text("输入内容")
                            .font(.headline)
                        TextEditor(text: $sourceText)
                            .frame(minHeight: 120)
                            .padding(8)
                            .background(Color(.systemGray6))
                            .cornerRadius(12)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color(.systemGray4), lineWidth: 1)
                            )
                    }
                    .padding(.horizontal)

                    // Character Selection
                    VStack(alignment: .leading, spacing: 8) {
                        Text("选择角色")
                            .font(.headline)
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 12) {
                            ForEach(characters, id: \.id) { char in
                                Button(action: { selectedCharacter = char.id }) {
                                    VStack(spacing: 4) {
                                        Text(char.emoji)
                                            .font(.system(size: 36))
                                        Text(char.name)
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(
                                        selectedCharacter == char.id
                                            ? Color.purple.opacity(0.1)
                                            : Color(.systemGray6)
                                    )
                                    .cornerRadius(12)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 12)
                                            .stroke(
                                                selectedCharacter == char.id
                                                    ? Color.purple
                                                    : Color.clear,
                                                lineWidth: 2
                                            )
                                    )
                                }
                            }
                        }
                    }
                    .padding(.horizontal)

                    // Generate Button
                    Button(action: generateVideo) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .tint(.white)
                            }
                            Text(isLoading ? "生成中..." : "✨ 生成动漫视频")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            LinearGradient(
                                colors: [.purple, .pink],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .foregroundColor(.white)
                        .cornerRadius(16)
                    }
                    .disabled(sourceText.isEmpty || isLoading)
                    .padding(.horizontal)

                    // Result
                    if let url = resultVideoURL {
                        VStack(spacing: 12) {
                            Text("✨ 生成完成！")
                                .font(.headline)
                            Text("视频已生成，请在浏览器中查看")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            Link("打开视频", destination: URL(string: url)!)
                                .font(.headline)
                                .foregroundColor(.blue)
                        }
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(16)
                        .padding(.horizontal)
                    }
                }
                .padding(.bottom, 40)
            }
            .navigationBarHidden(true)
            .background(
                LinearGradient(
                    colors: [Color.pink.opacity(0.05), Color.purple.opacity(0.05)],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
            )
        }
    }

    func generateVideo() {
        isLoading = true
        // TODO: 调用后端 API
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            isLoading = false
        }
    }
}

#Preview {
    ContentView()
}
