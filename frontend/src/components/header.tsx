import Link from "next/link";
import { Mail } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Mail className="h-6 w-6" />
          <span className="font-semibold text-lg">Email Classifier</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">
            Início
          </Link>
          <Link href="/emails" className="text-sm font-medium hover:text-primary transition-colors">
            Emails
          </Link>
          <Link href="/about" className="text-sm font-medium hover:text-primary transition-colors">
            Sobre
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link href="/" className="md:hidden">
            <Button variant="outline" size="icon">
              <Mail className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
