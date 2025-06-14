import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { trpc } from '../utils/trpc'
import { httpBatchLink } from '@trpc/client'
import superjson from 'superjson'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import kaltireLogo from '../images/kaltire_logo.png'

function MyApp({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient())
  const [trpcClient] = useState(() =>
    trpc.createClient({
      transformer: superjson,
      links: [
        httpBatchLink({ url: '/api/trpc' }),
      ],
    })
  )

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        <div className="app-container">
          <header className="header">
            <Image src={kaltireLogo} alt="Kaltire" className="logo" />
            <nav>
              <Link href="/" className="nav-link">Chatbot</Link>
              <Link href="/config" className="nav-link">Configuration</Link>
            </nav>
          </header>
          <Component {...pageProps} />
        </div>
      </QueryClientProvider>
    </trpc.Provider>
  )
}

export default MyApp
