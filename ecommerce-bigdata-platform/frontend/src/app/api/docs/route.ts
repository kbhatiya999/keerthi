import { getApiDocs } from "@/lib/swagger";

export async function GET() {
  const spec = await getApiDocs();
  return new Response(JSON.stringify(spec), {
    headers: { "Content-Type": "application/json" },
  });
}
