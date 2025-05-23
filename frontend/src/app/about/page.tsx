import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sobre | Classificador de Emails",
  description: "Informações sobre o projeto de classificação de emails",
};

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-card rounded-lg border p-6 shadow-sm space-y-6">
        <section>
          <h2 className="text-2xl font-semibold mb-3">Como funciona o isolamento</h2>
          <p className="text-base text-muted-foreground mb-4">
            O sistema analisa o conteúdo do email, incluindo assunto e corpo da mensagem, para determinar
            se é um email que requer atenção imediata (produtivo) ou se é um email informativo ou de
            agradecimento que não exige ação urgente (improdutivo).
          </p>
          <p className="text-base text-muted-foreground">
            A classificação é feita através de uma combinação de heurísticas e modelos de linguagem avançados
            da Gemini para analisar o contexto completo de cada mensagem.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-3">Privacidade e Segurança</h2>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <h3 className="text-lg font-medium text-green-800 mb-2">Isolamento Automático por Usuário</h3>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Cada usuário vê apenas seus próprios emails classificados</li>
              <li>• Isolamento baseado no seu endereço IP</li>
              <li>• Nenhum email é compartilhado entre diferentes usuários</li>
              <li>• Sistema funciona sem necessidade de cadastro ou login</li>
            </ul>
          </div>
          <p className="text-base text-muted-foreground">
            Seus dados estão protegidos e privados. O sistema garante que somente você tenha acesso
            aos emails que submeter para classificação.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-3">Tecnologias Utilizadas</h2>
          <ul className="list-disc pl-6 text-muted-foreground space-y-2">
            <li>Backend: Django (Python)</li>
            <li>Frontend: Next.js (React)</li>
            <li>Estilização: TailwindCSS e shadcn/ui</li>
            <li>IA: Google Gemini</li>
            <li>Segurança: Isolamento por IP, Rate Limiting, CORS</li>
            <li>Infraestrutura: Railway (Backend), Vercel (Frontend)</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
