import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import api from "../../lib/axios";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Card } from "../../components/ui/card";

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(3),
});

export default function Register() {
  const navigate = useNavigate();

  const form = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (values) => {
    try {
      await api.post("/auth/register", values);
      navigate("/login");
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center">
      <Card className="p-6 w-[380px] space-y-4">
        <h2 className="text-xl font-bold">Create Account</h2>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <Input placeholder="Name" {...form.register("name")} />
          <Input placeholder="Email" {...form.register("email")} />
          <Input
            type="password"
            placeholder="Password"
            {...form.register("password")}
          />

          <Button className="w-full" type="submit">
            Register
          </Button>
        </form>
        <p className="text-sm text-center">
          Already have an account?{" "}
          <a href="/login" className="text-blue-500">
            Login
          </a>
        </p>
      </Card>
    </div>
  );
}
