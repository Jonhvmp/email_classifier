import { Metadata } from "next";
import EmailsPageClient from "@/components/emails-page-client";

export const metadata: Metadata = {
  title: "Lista de Emails | Classificador de Emails",
  description: "Visualize todos os emails classificados pelo sistema",
};

export default function EmailsPage() {
  return <EmailsPageClient />;
}
