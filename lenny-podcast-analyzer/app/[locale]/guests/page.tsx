import Link from "next/link";
import { getGuests } from "../../../lib/site-data";

export default function GuestsPage({ params }: { params: { locale: string } }) {
  const guests = getGuests(params.locale);

  return (
    <section>
      <h2>Guests</h2>
      <ul>
        {guests.map((guest) => (
          <li key={guest.slug}>
            <Link href={`/${params.locale}/episodes/${guest.episode_slug}`}>
              {guest.name}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
