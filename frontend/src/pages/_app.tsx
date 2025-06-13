import '../styles/globals.css'
import type { AppProps } from 'next/app'
import Link from 'next/link'
import Image from 'next/image'
import kaltireLogo from '../images/kaltire_logo.png'

function MyApp({ Component, pageProps }: AppProps) {
  return (
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
  )
}

export default MyApp
