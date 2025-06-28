/** 
 * @swagger
 * /api/health:
 *   get:
 *     description: Alive check
 *     responses:
 *       200:
 *         description: OK
 */
export async function GET() {
  return new Response(JSON.stringify({ status: "OK" }), { status: 200 });
}
