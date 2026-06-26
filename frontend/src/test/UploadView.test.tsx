import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { UploadView } from "../components/UploadView";

describe("UploadView", () => {
  it("muestra el encabezado y deshabilita el botón sin archivo", () => {
    render(<UploadView onSubmit={vi.fn()} busy={false} error={null} />);
    expect(screen.getByText(/Da voz a tu vídeo/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Transcribir vídeo/i })).toBeDisabled();
  });

  it("habilita y envía cuando hay archivo", () => {
    const onSubmit = vi.fn();
    const { container } = render(<UploadView onSubmit={onSubmit} busy={false} error={null} />);

    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["data"], "clip.mp4", { type: "video/mp4" });
    fireEvent.change(input, { target: { files: [file] } });

    const button = screen.getByRole("button", { name: /Transcribir vídeo/i });
    expect(button).toBeEnabled();
    fireEvent.click(button);

    expect(onSubmit).toHaveBeenCalledWith(file, "auto", "small");
  });

  it("muestra el mensaje de error", () => {
    render(<UploadView onSubmit={vi.fn()} busy={false} error="El archivo supera el límite" />);
    expect(screen.getByText(/supera el límite/i)).toBeInTheDocument();
  });
});
