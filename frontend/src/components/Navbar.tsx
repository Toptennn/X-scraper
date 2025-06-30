import Link from 'next/link'

export default function Navbar() {
  return (
    <nav className="bg-gray-800 text-white p-4 flex justify-between">
      <div className="font-bold">X Scraper</div>
      <div className="space-x-4">
        <Link href="/dashboard" className="hover:underline">Dashboard</Link>
        <Link href="/login" className="hover:underline">Login</Link>
        <Link href="/signup" className="hover:underline">Sign Up</Link>
      </div>
    </nav>
  )
}
