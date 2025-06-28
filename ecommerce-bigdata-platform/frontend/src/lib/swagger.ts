import { createSwaggerSpec } from "next-swagger-doc";

export const getApiDocs = async () =>
  createSwaggerSpec({
    apiFolder: "src/app/api",             // where your Next.js API routes live
    definition: {
      openapi: "3.0.0",
      info: { title: "Frontend BFF", version: "1.0.0" },
    },
  });
