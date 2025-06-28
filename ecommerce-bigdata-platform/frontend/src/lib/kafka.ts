import { Kafka } from "kafkajs";

export const kafkaProducer = (() => {
  if (typeof window === "undefined") return null;   // SSR guard
  const kafka = new Kafka({
    clientId: "frontend",
    brokers: [process.env.KAFKA_BROKER!],
    ssl: true,
    sasl: { mechanism: "plain", username: process.env.KAFKA_API_KEY!, password: process.env.KAFKA_API_SECRET! },
  });
  const producer = kafka.producer();
  producer.connect();
  return producer;
})();
