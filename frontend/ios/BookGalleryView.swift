import SwiftUI

struct BookGalleryView: View {
    @State private var searchText = ""

    let curatedBooks = [
        BookItem(id: "rich_dad_poor_dad", title: "Rich Dad Poor Dad", author: "Robert Kiyosaki", price: 12.99, category: "Financial Mindset"),
        BookItem(id: "art_of_war", title: "The Art of War", author: "Sun Tzu", price: 9.99, category: "Strategic Calm"),
        BookItem(id: "atomic_habits", title: "Atomic Habits", author: "James Clear", price: 14.99, category: "Discipline")
    ]

    var body: some View {
        NavigationView {
            ZStack {
                Color(UIColor.systemBackground).ignoresSafeArea()

                VStack(spacing: 24) {
                    Text("Consciousness Gallery")
                        .font(.title2)
                        .foregroundStyle(.secondary)
                        .padding(.top, 20)

                    TextField("Search books", text: $searchText)
                        .textFieldStyle(.roundedBorder)
                        .padding(.horizontal)

                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(curatedBooks) { book in
                                BookCard(book: book)
                            }
                        }
                        .padding(.horizontal)
                    }

                    Button(action: {
                        // Voice command to find or add a book
                    }) {
                        HStack {
                            Image(systemName: "mic.circle.fill")
                            Text("Speak to find or add a book")
                        }
                    }
                    .foregroundStyle(.blue)
                    .padding(.bottom, 24)
                }
            }
        }
    }
}

struct BookCard: View {
    let book: BookItem

    var body: some View {
        HStack(spacing: 16) {
            Rectangle()
                .fill(Color.gray.opacity(0.3))
                .frame(width: 60, height: 80)
                .cornerRadius(8)

            VStack(alignment: .leading, spacing: 6) {
                Text(book.title).font(.headline)
                Text(book.author).font(.subheadline).foregroundStyle(.secondary)
                Text(book.category).font(.caption).foregroundStyle(.blue.opacity(0.8))
            }

            Spacer()

            VStack {
                Text("$\(book.price, specifier: "%.2f")").bold()
                Button("Add") {
                    // Call POST /books/add endpoint
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.small)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(12)
    }
}

struct BookItem: Identifiable {
    let id: String
    let title: String
    let author: String
    let price: Double
    let category: String
}
