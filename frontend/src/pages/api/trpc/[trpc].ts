import { createNextApiHandler } from '@trpc/server/adapters/next'
import { initTRPC } from '@trpc/server'
import { z } from 'zod'

const t = initTRPC.create()

export const appRouter = t.router({
  sendMessage: t.procedure
    .input(z.object({ message: z.string() }))
    .mutation(async ({ input }) => {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input.message }),
      })
      const data = await res.json()
      return data
    }),
})

export type AppRouter = typeof appRouter

export default createNextApiHandler({ router: appRouter })
