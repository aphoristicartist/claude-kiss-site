export async function onRequest({ request, env }) {
  const page = await env.ASSETS.fetch(new URL("/404", request.url));
  const headers = new Headers(page.headers);

  headers.set("Cache-Control", "no-store, no-transform");

  if (request.method !== "GET" && request.method !== "HEAD") {
    headers.set("Allow", "GET, HEAD");
    headers.set("Content-Type", "text/plain; charset=utf-8");
    headers.delete("Content-Length");

    return new Response("Method not allowed\n", {
      status: 405,
      statusText: "Method Not Allowed",
      headers,
    });
  }

  return new Response(request.method === "HEAD" ? null : page.body, {
    status: 404,
    statusText: "Not Found",
    headers,
  });
}
