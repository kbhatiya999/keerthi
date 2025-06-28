import dynamic from "next/dynamic";
import { getApiDocs } from "@/lib/swagger";
import "swagger-ui-react/swagger-ui.css";

const SwaggerUI = dynamic(import("swagger-ui-react"), { ssr: false });

export default async function ApiDocs() {
  const spec = await getApiDocs();
  return <SwaggerUI spec={spec} />;
}
