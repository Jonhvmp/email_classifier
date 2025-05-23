import { Metadata } from "next";
import { EmailDetail } from "@/components/email-detail";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { use } from "react";

type Props = {
  params: Promise<{
    id: string;
  }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  // Usar desestruturação após o await
  const { id } = await params;

  return {
    title: `Email #${id} | Classificador de Emails`,
    description: "Detalhes do email classificado",
  };
}

export default function EmailDetailPage(props: Props) {
  // Usar o hook 'use' do React para consumir a Promise
  const { params } = props;
  const { id } = use(params);

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
        <h1 className="text-2xl font-bold mb-6">Detalhes do Email #{id}</h1>
        <EmailDetail id={id} />
      </div>
    </div>
  );
}
