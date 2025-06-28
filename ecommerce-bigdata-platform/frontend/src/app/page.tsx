import Image from "next/image";
import { api } from "@/lib/api";

type Product = { _id: string; name: string; price: number; description: string };

export default async function Home() {
  const products = await api<Product[]>("/products/");

  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <h1 className="text-3xl font-bold mb-8">E-Commerce Products</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((p) => (
          <div
            key={p._id}
            className="border rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold mb-2">{p.name}</h2>
            <p className="text-gray-600 mb-4">{p.description}</p>
            <p className="text-lg font-bold text-blue-600">${p.price}</p>
            <button
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
              onClick={async () => {
                // Example Kafka event
                try {
                  const { kafkaProducer } = await import("@/lib/kafka");
                  await kafkaProducer?.send({
                    topic: "clickstream",
                    messages: [
                      { value: JSON.stringify({ event: "add_to_cart", productId: p._id }) },
                    ],
                  });
                } catch (error) {
                  console.error("Failed to send Kafka event:", error);
                }
              }}
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
