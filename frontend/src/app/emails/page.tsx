import { Metadata } from "next";
import EmailList from "@/components/email-list";
import { Pagination } from "@/components/ui/pagination";

export const metadata: Metadata = {
  title: "Lista de Emails | Classificador de Emails",
  description: "Visualize todos os emails classificados pelo sistema",
};

export default function EmailsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Emails Classificados</h1>
      <div className="bg-card rounded-lg border p-6 shadow-sm">
        <EmailList />
        <div className="mt-6 flex justify-center">
          <Pagination />
        </div>
      </div>
    </div>
  );
}
