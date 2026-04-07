import SwiftUI

struct BookGalleryView: View {
    @State private var searchText = ""

    let curatedBooks = [
        BookItem(
            id: "rich_dad_poor_dad",
            title: "Rich Dad Poor Dad",
            author: "Robert Kiyosaki",
            price: 12.99,
            category: "Financial Mindset",
            consciousness: "Asset-focused thinking, making money work for you, long-term wealth building."
        ),
        BookItem(
            id: "art_of_war",
            title: "The Art of War",
            author: "Sun Tzu",
            price: 9.99,
            category: "Strategic Calm",
            consciousness: "Composure under pressure, strategic patience, winning without unnecessary conflict."
        ),
        BookItem(
            id: "atomic_habits",
            title: "Atomic Habits",
            author: "James Clear",
            price: 14.99,
            category: "Discipline & Growth",
            consciousness: "Small consistent actions, identity-based change, building systems."
        )
    ]

    var filteredBooks: [BookItem] {
        searchText.isEmpty ? curatedBooks : curatedBooks.filter {
            $0.title.localizedCaseInsensitiveContains(searchText) ||
            $0.category.localizedCaseInsensitiveContains(searchText) ||
            $0.consciousness.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationView {
            ZStack {
                Color(UIColor.systemBackground).ignoresSafeArea()

                VStack(spacing: 20) {
                    Text("Consciousness Gallery")
                        .font(.title2)
                        .foregroundStyle(.secondary)
                        .padding(.top, 20)

                    TextField("Search books or consciousness types", text: $searchText)
                        .textFieldStyle(.roundedBorder)
                        .padding(.horizontal)

                    ScrollView {
                        LazyVStack(spacing: 18) {
                            ForEach(filteredBooks) { book in
                                BookCard(book: book)
                            }
                        }
                        .padding(.horizontal)
                    }

                    Button("Speak to find or add a book") {
                        // Voice command handler
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
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 14) {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .frame(width: 70, height: 90)
                    .cornerRadius(8)

                VStack(alignment: .leading, spacing: 6) {
                    Text(book.title).font(.headline)
                    Text(book.author).font(.subheadline).foregroundStyle(.secondary)
                    Text(book.category).font(.caption).foregroundStyle(.blue)
                }

                Spacer()
            }

            Text(book.consciousness)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(3)

            HStack {
                Text("$\(book.price, specifier: "%.2f")").bold()
                Spacer()
                Button("Add to My Consciousness") {
                    // Call POST /books/add with book.id and priority
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .cornerRadius(16)
    }
}

struct BookItem: Identifiable {
    let id: String
    let title: String
    let author: String
    let price: Double
    let category: String
    let consciousness: String
}
