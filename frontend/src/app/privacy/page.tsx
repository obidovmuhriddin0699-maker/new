import type { Metadata } from "next";

import { Contact, LegalPage, legalInfo } from "@/components/legal/LegalPage";

export const dynamic = "force-dynamic"; // operator / contact come from the server environment
export const metadata: Metadata = { title: "Privacy Policy" };

export default function PrivacyPage() {
  const { operator, site } = legalInfo();
  const status = site ? `${site.replace(/\/$/, "")}/api/meta/data-deletion-status?code=…` : "/api/meta/data-deletion-status?code=…";
  return (
    <LegalPage title="Privacy Policy / Maxfiylik siyosati">
      <section>
        <h2>1. Who we are</h2>
        <p>
          This application (&quot;MUXRIDDIN AI Instagram Manager&quot;) is operated by {operator} to plan, draft and — only after
          explicit human approval — publish content to the operator&apos;s own Instagram professional account through the
          official Meta (Instagram) API. It is a private tool for the operator&apos;s team; it is not offered to the public.
        </p>
      </section>
      <section>
        <h2>2. Data we process</h2>
        <ul>
          <li>Instagram account identifiers you authorise via Meta&apos;s official login (account ID, username, account type, profile picture URL).</li>
          <li>An access token issued by Meta, stored only in encrypted form and used solely to call the Instagram API on your behalf.</li>
          <li>Insights returned by the Instagram API for the connected account and its posts (e.g. reach, views, likes, comments, saves). Metrics the API does not return are never estimated.</li>
          <li>Content created in the app (texts, media you upload) and an audit log of actions taken by the team.</li>
        </ul>
        <p>We never ask for or store Instagram passwords. We do not access other people&apos;s accounts or private messages.</p>
      </section>
      <section>
        <h2>3. How we use it</h2>
        <p>
          Only to provide the app&apos;s functions: preparing content, publishing approved content, showing analytics and
          keeping a security audit trail. We do not sell or rent data and do not use it for advertising.
        </p>
      </section>
      <section>
        <h2>4. Sharing</h2>
        <p>
          Data is sent to Meta only as required to publish and read insights through the Instagram API. AI drafting runs on
          a self-hosted model; content is not sent to third-party AI services unless the operator configures one.
          Infrastructure providers (server hosting) process data on our behalf.
        </p>
      </section>
      <section>
        <h2>5. Retention and deletion</h2>
        <p>
          Tokens are deleted when the account is disconnected or when Meta notifies us that you removed the app. You can
          request deletion of your data at any time: remove the app in Instagram (Settings → Website permissions → Apps
          and websites) — Meta then sends us a data deletion request and you receive a confirmation code you can check at{" "}
          <code className="break-all">{status}</code> — or contact us at <Contact />.
        </p>
      </section>
      <section>
        <h2>6. Security</h2>
        <p>Encryption of tokens at rest, HTTPS, access limited to authorised team members, rate limiting and an append-only audit log.</p>
      </section>
      <section>
        <h2>7. Contact</h2>
        <p>Questions or requests: <Contact />.</p>
      </section>
      <section lang="uz">
        <h2>Qisqacha (o‘zbekcha)</h2>
        <p>
          Ilova faqat egasining Instagram professional akkaunti uchun, rasmiy Meta API orqali ishlaydi. Instagram paroli
          so‘ralmaydi va saqlanmaydi. Token faqat shifrlangan holda saqlanadi. Ma’lumotlar sotilmaydi va reklama uchun
          ishlatilmaydi. Ma’lumotlarni o‘chirish uchun Instagram sozlamalarida ilovani olib tashlang yoki biz bilan
          bog‘laning: <Contact />.
        </p>
      </section>
    </LegalPage>
  );
}
