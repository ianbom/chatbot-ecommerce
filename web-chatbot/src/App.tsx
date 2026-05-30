import { Navigate, Route, Routes } from "react-router-dom"

import { DashboardRoute } from "@/pages/dashboard"
import { OrdersRoute } from "@/pages/orders"
import { ProductsRoute } from "@/pages/products"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardRoute />} />
      <Route path="/products" element={<ProductsRoute />} />
      <Route path="/orders" element={<OrdersRoute />} />
    </Routes>
  )
}

export default App
