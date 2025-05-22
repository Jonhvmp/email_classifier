import { Metadata } from "next";
import { EmailDetail } from "@/components/email-detail";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

type Props = {
  params: {
    id: string;
  };
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  // Correctly access params in async function
  return {
    title: `Email #${params.id} | Classificador de Emails`,
    description: "Detalhes do email classificado",
  };
}

export default function EmailDetailPage({ params }: Props) {
  // Remove 'async' and directly use params without await
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/emails">
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Voltar para lista
          </Button>
        </Link>
      </div>

      <div className="bg-card rounded-lg border p-6 shadow-sm">
        <h1 className="text-2xl font-bold mb-6">Detalhes do Email #{params.id}</h1>
        <EmailDetail id={params.id} />
      </div>
    </div>
  );
}
