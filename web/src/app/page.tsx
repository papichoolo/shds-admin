import { redirect } from "next/navigation";

export default function Home() {
  // Redirect root to /login for now
  redirect("/login");
}
