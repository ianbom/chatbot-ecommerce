import { Navigate, Route, Routes } from "react-router-dom"

import { ProtectedRoute, PublicOnlyRoute } from "@/auth/protected-route"
import { CustomersRoute } from "@/pages/customers"
import { DashboardRoute } from "@/pages/dashboard"
import { LeadsRoute } from "@/pages/leads"
import { LoginRoute } from "@/pages/login"
import { OrdersRoute } from "@/pages/orders"
import { ProductsRoute } from "@/pages/products"
import { RegisterRoute } from "@/pages/register"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginRoute />} />
        <Route path="/register" element={<RegisterRoute />} />
      </Route>
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardRoute />} />
        <Route path="/products" element={<ProductsRoute />} />
        <Route path="/orders" element={<OrdersRoute />} />
        <Route path="/customers" element={<CustomersRoute />} />
        <Route path="/leads" element={<LeadsRoute />} />
      </Route>
    </Routes>
  )
}

export default App
