import { Metadata } from "next";
import { EmailsPageClient } from "@/components/emails-page-client";

export const metadata: Metadata = {
  title: "Emails Classificados | Classificador de Emails",
  description: "Lista de emails classificados pelo sistema de IA",
};

export default function EmailsPage() {
  return <EmailsPageClient />;
}
