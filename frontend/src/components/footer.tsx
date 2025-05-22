import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-muted/40">
      <div className="container flex flex-col sm:flex-row py-6 items-center justify-between">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Email Classifier
          </p>
        </div>
        <div className="flex items-center mt-4 sm:mt-0 gap-4">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            Início
          </Link>
          <Link href="/emails" className="text-sm text-muted-foreground hover:text-foreground">
            Emails
          </Link>
          <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground">
            Sobre
          </Link>
        </div>
      </div>
    </footer>
  );
}
