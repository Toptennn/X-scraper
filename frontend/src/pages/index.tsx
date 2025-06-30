import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow flex items-center justify-center flex-col space-y-4">
        <h1 className="text-3xl font-bold">Welcome to X Scraper</h1>
        <Link href="/login" className="bg-blue-600 text-white px-4 py-2 rounded">Get Started</Link>
      </main>
      <Footer />
    </div>
  )
}
