"use client";

import Link from "next/link";
import { Mail, Home, Inbox, Info } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { Button } from "./ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo e título com margem lateral ajustada */}
        <div className="flex items-center ml-4 md:ml-10">
          <Link href="/" className="flex items-center gap-2">
            <Mail className="h-6 w-6" />
            <span className="font-bold text-lg tracking-tight">Email Classifier</span>
          </Link>
        </div>

        {/* Menu para desktop - centralizado */}
        <nav className="hidden md:flex items-center gap-8">
          <Link href="/" className="nav-link text-sm hover:text-primary transition-colors">
            Início
          </Link>
          <Link href="/emails" className="nav-link text-sm hover:text-primary transition-colors">
            Emails
          </Link>
          <Link href="/about" className="nav-link text-sm hover:text-primary transition-colors">
            Sobre
          </Link>
        </nav>

        {/* Ícones para mobile */}
        <nav className="md:hidden flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="icon">
              <Home className="h-5 w-5" />
            </Button>
          </Link>
          <Link href="/emails">
            <Button variant="ghost" size="icon">
              <Inbox className="h-5 w-5" />
            </Button>
          </Link>
          <Link href="/about">
            <Button variant="ghost" size="icon">
              <Info className="h-5 w-5" />
            </Button>
          </Link>
        </nav>

        {/* Toggle de tema com margem adequada */}
        <div className="flex items-center mr-4 md:mr-10">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
