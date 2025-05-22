import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sobre | Classificador de Emails",
  description: "Informações sobre o projeto de classificação de emails",
};

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Sobre o Projeto</h1>

      <div className="bg-card rounded-lg border p-6 shadow-sm space-y-6">
        <section>
          <h2 className="text-2xl font-semibold mb-3">O que é o Classificador de Emails?</h2>
          <p className="text-base text-muted-foreground">
            O Classificador de Emails é uma ferramenta que usa inteligência artificial para classificar
            automaticamente emails em duas categorias: produtivos e improdutivos.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-3">Como funciona?</h2>
          <p className="text-base text-muted-foreground mb-4">
            O sistema analisa o conteúdo do email, incluindo assunto e corpo da mensagem, para determinar
            se é um email que requer atenção imediata (produtivo) ou se é um email informativo ou de
            agradecimento que não exige ação urgente (improdutivo).
          </p>
          <p className="text-base text-muted-foreground">
            A classificação é feita através de uma combinação de heurísticas e modelos de linguagem avançados
            da Cohere e Hugging Face para analisar o contexto completo de cada mensagem.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-3">Tecnologias Utilizadas</h2>
          <ul className="list-disc pl-6 text-muted-foreground space-y-2">
            <li>Backend: Django (Python)</li>
            <li>Frontend: Next.js (React)</li>
            <li>Estilização: TailwindCSS e shadcn/ui</li>
            <li>IA: Cohere API e Hugging Face</li>
          </ul>
        </section>
      </div>
    </div>
  );
}
