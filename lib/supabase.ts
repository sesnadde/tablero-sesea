import "server-only";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SECRET_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error("No se encontraron las credenciales de Supabase.");
}

// Cliente de servidor únicamente: SUPABASE_SECRET_KEY omite RLS y
// nunca debe llegar al navegador.
export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: { persistSession: false }
});
