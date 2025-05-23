import Link from "next/link";
import { Github, Linkedin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t bg-muted/40">
      <div className="container mx-auto px-4 py-4 md:py-6">
        {/* Layout para mobile (coluna) e desktop (linha) */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          {/* Links de navegação - À esquerda no desktop */}
          <div className="flex justify-center md:justify-start mb-4 md:mb-0">
            <nav className="flex gap-4 md:gap-6">
              <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
                Início
              </Link>
              <Link href="/emails" className="text-sm text-muted-foreground hover:text-foreground">
                Emails
              </Link>
              <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground">
                Sobre
              </Link>
            </nav>
          </div>

          {/* Copyright - Centralizado no desktop */}
          <div className="flex justify-center mb-4 md:mb-0">
            <p className="text-xs text-muted-foreground text-center">
              &copy; {new Date().getFullYear()} Email Classifier • Desenvolvido por{" "}
              <Link
                href="https://github.com/jonhvmp"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground underline underline-offset-2"
              >
                Jonh Alex
              </Link>
            </p>
          </div>

          {/* Redes sociais - À direita no desktop */}
          <div className="flex justify-center md:justify-end">
            <div className="flex gap-4">
              <Link
                href="https://github.com/jonhvmp"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </Link>
              <Link
                href="https://linkedin.com/in/jonhvmp"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
