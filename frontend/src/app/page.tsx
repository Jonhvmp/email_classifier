import { Metadata } from "next";
import EmailSubmissionForm from "@/components/email-submission-form";
import { BackendInfo } from "@/components/backend-info";
import { ApiUsageMonitor } from "@/components/api-usage-monitor";
import { QueueStatusDialog } from "@/components/queue-status-dialog";

export const metadata: Metadata = {
  title: "Classificador de Emails",
  description: "Classificador de emails que diferencia entre produtivos e improdutivos",
};

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Classificador de Emails
      </h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <div className="mb-4">
              <h2 className="text-xl font-semibold mb-2">
                Submeta um email para classificação
              </h2>
              <p className="text-muted-foreground">
                Insira o conteúdo do email ou faça upload de um arquivo para classificação
                automática entre produtivo e improdutivo.
              </p>
            </div>
            <EmailSubmissionForm />
          </div>
        </div>
        <div className="space-y-6">
          <BackendInfo />
          <ApiUsageMonitor />
          <QueueStatusDialog />
        </div>
      </div>
    </div>
  );
}
