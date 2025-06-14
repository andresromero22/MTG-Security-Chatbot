import { createNextApiHandler } from '@trpc/server/adapters/next'
import { initTRPC } from '@trpc/server'
import superjson from 'superjson'
import { z } from 'zod'

const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const t = initTRPC.create({
  transformer: superjson,
})

export const appRouter = t.router({
  sendMessage: t.procedure
    .input(z.object({ message: z.string() }))
    .mutation(async ({ input }) => {
      const res = await fetch(`${baseURL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input.message }),
      })
      const data = await res.json()
      return data
    }),
  listManuals: t.procedure.query(async () => {
    const res = await fetch(`${baseURL}/manuals`)
    const data = await res.json()
    return data.files as string[]
  }),
  deleteManual: t.procedure
    .input(z.object({ filename: z.string() }))
    .mutation(async ({ input }) => {
      await fetch(`${baseURL}/manuals/${encodeURIComponent(input.filename)}`, {
        method: 'DELETE',
      })
      return true
    }),
})

export type AppRouter = typeof appRouter

export default createNextApiHandler({ router: appRouter })
