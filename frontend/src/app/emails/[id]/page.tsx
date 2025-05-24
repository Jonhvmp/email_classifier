import { Metadata } from "next";
import { EmailDetail } from "@/components/email-detail";
import { use } from "react";

type Props = {
  params: Promise<{
    id: string;
  }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;

  return {
    title: `Email #${id} | Classificador de Emails`,
    description: "Detalhes do email classificado",
  };
}

export default function EmailDetailPage(props: Props) {
  const { params } = props;
  const { id } = use(params);

  return <EmailDetail id={parseInt(id)} />;
}
