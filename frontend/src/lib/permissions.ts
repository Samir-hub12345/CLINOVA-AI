import { UserRole } from "@/types";

export const dashboardForRole: Record<UserRole, string> = {
  patient: "/dashboard/patient",
  doctor: "/dashboard/doctor",
  admin: "/dashboard/admin",
  nurse: "/dashboard/nurse",
  staff: "/dashboard/staff",
};
export function dashboardPath(role: UserRole): string {
  return dashboardForRole[role] || "/unauthorized";
}
type NavItem = { label: string; href: string };
export const navigationByRole: Record<UserRole, NavItem[]> = {
  patient: [
    { label: "My Dashboard", href: "/dashboard/patient" },
    { label: "Start Intake", href: "/intake" },
    { label: "Documents", href: "/documents" },
    { label: "My Profile", href: "/portal/profile" },
  ],
  doctor: [
    { label: "Doctor Dashboard", href: "/dashboard/doctor" },
    { label: "Review Queue", href: "/review" },
    { label: "EHR Directory", href: "/patients" },
    { label: "Consultations", href: "/consultations" },
    { label: "AI Triage", href: "/triage" },
    { label: "Documents", href: "/documents" },
  ],
  nurse: [
    { label: "Nurse Station", href: "/dashboard/nurse" },
    { label: "Patient Intake", href: "/intake" },
    { label: "Review Queue", href: "/review" },
    { label: "Patients", href: "/patients" },
    { label: "Front Desk Console", href: "/dashboard/staff" },
    { label: "Documents", href: "/documents" },
  ],
  staff: [
    { label: "Front Desk Console", href: "/dashboard/staff" },
    { label: "Patient Registration", href: "/intake" },
    { label: "Review & Routing", href: "/review" },
    { label: "Patient Directory", href: "/patients" },
    { label: "Nurse Station", href: "/dashboard/nurse" },
    { label: "Documents", href: "/documents" },
  ],
  admin: [
    { label: "Admin Console", href: "/dashboard/admin" },
    { label: "Audit Trail", href: "/audit" },
    { label: "Documents", href: "/documents" },
  ],
};
const allRoles: UserRole[] = ["patient", "doctor", "nurse", "admin", "staff"];
const clinical: UserRole[] = ["doctor", "nurse", "staff"];
const protectedPrefixes: [string, UserRole[]][] = [
  ["/dashboard/patient", ["patient"]],
  ["/dashboard/doctor", ["doctor"]],
  ["/dashboard/admin", ["admin"]],
  ["/dashboard/nurse", ["nurse", "staff"]],
  ["/dashboard/staff", ["staff", "nurse"]],
  ["/dashboard", allRoles],
  ["/portal", ["patient"]],
  ["/patients/profile", ["patient"]],
  ["/patients", clinical],
  ["/review", clinical],
  ["/consultations", ["doctor", "nurse"]],
  ["/triage", ["doctor"]],
  ["/audit", ["admin"]],
  ["/intake", ["patient", "doctor", "nurse", "staff"]],
  ["/documents", allRoles],
];
export function rolesForPath(path: string): UserRole[] | null {
  return protectedPrefixes.find(([prefix]) => path === prefix || path.startsWith(prefix + "/"))?.[1] ?? null;
}