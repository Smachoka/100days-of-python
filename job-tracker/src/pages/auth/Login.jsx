import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import api from "../../lib/axios";
import { useAuthStore } from "../../store/authStore";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Card } from "../../components/ui/card";
import { useNavigate } from "react-router-dom";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(3),
});

export default function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const form = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (values) => {
    try {
      const res = await api.post("/auth/login", values);
      setAuth(res.data.user, res.data.token);
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center">
      <Card className="p-6 w-[380px] space-y-4">
        <h2 className="text-xl font-bold">Login</h2>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <Input placeholder="Email" {...form.register("email")} />
          <Input
            type="password"
            placeholder="Password"
            {...form.register("password")}
          />

          <Button className="w-full" type="submit">
            Login
          </Button>
        </form>
        <p className="text-sm text-center">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-500">
            Register
          </a>
        </p>
      </Card>
    </div>
  );
}
