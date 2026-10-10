import { forwardSignedRequest } from "../forward";

// Data Deletion Request URL. Meta expects JSON { url, confirmation_code } back.
export function POST(request: Request): Promise<Response> {
  return forwardSignedRequest(request, "data-deletion");
}
