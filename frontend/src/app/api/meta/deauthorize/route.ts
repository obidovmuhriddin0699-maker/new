import { forwardSignedRequest } from "../forward";

// Deauthorize Callback URL (Meta App Dashboard → Instagram → Business login settings).
export function POST(request: Request): Promise<Response> {
  return forwardSignedRequest(request, "deauthorize");
}
