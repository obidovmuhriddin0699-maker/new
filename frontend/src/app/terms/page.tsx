import type { Metadata } from "next";

import { Contact, LegalPage, legalInfo } from "@/components/legal/LegalPage";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Terms of Service" };

export default function TermsPage() {
  const { operator } = legalInfo();
  return (
    <LegalPage title="Terms of Service / Foydalanish shartlari">
      <section>
        <h2>1. Service</h2>
        <p>
          MUXRIDDIN AI Instagram Manager is a private content-management tool operated by {operator}. Access is limited to
          accounts created by the operator; there is no public sign-up.
        </p>
      </section>
      <section>
        <h2>2. Human approval</h2>
        <p>
          AI features only draft, plan and analyse. Nothing is published without an explicit approval by an authorised
          person, who remains responsible for the published content and its compliance with Instagram&apos;s Terms of Use
          and Community Guidelines.
        </p>
      </section>
      <section>
        <h2>3. Instagram and Meta</h2>
        <p>
          The service uses the official Instagram API under Meta&apos;s Platform Terms. Features Meta does not offer through its
          API are not provided. Availability depends on Meta&apos;s API and policies.
        </p>
      </section>
      <section>
        <h2>4. Acceptable use</h2>
        <ul>
          <li>Use only Instagram accounts you own or are authorised to manage.</li>
          <li>Do not attempt to bypass security controls, rate limits or the approval process.</li>
        </ul>
      </section>
      <section>
        <h2>5. Liability</h2>
        <p>The service is provided as is. The operator is not liable for outages of Meta&apos;s services.</p>
      </section>
      <section>
        <h2>6. Contact</h2>
        <p><Contact /></p>
      </section>
    </LegalPage>
  );
}
