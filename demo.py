# -- coding: utf-8 --`
import argparse
import os
# engine
from stable_diffusion_engine import StableDiffusionEngine
# scheduler
from diffusers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler
# utils
import cv2
import numpy as np
import shlex


def main(args):
    print("initializing engine...")

    if args.scheduler.upper() == "LMS":
        scheduler_txt2img = LMSDiscreteScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            tensor_format="np"
        )
    elif args.scheduler.upper() == "DDIM":
        scheduler_txt2img = DDIMScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            tensor_format="np"
        )
    else:
        raise ValueError("Scheduler must be one of: [LMS, DDIM]")

    scheduler_img2img = PNDMScheduler(
        beta_start=args.beta_start,
        beta_end=args.beta_end,
        beta_schedule=args.beta_schedule,
        skip_prk_steps = True,
        tensor_format="np"
    )

    engine = StableDiffusionEngine(
        model = args.model,
        model_revision = args.model_revision,
        scheduler_txt2img = scheduler_txt2img,
        scheduler_img2img = scheduler_img2img,
        tokenizer = args.tokenizer
    )

    print("engine initialized")

    parser2 = argparse.ArgumentParser()
    # randomizer params
    parser2.add_argument("--seed", type=int, default=None, help="random seed for generating consistent images per prompt")
    # diffusion params
    parser2.add_argument("--num-inference-steps", type=int, default=20, help="num inference steps")
    parser2.add_argument("--guidance-scale", type=float, default=7.5, help="guidance scale")
    parser2.add_argument("--eta", type=float, default=0.0, help="eta")
    # prompt
    parser2.add_argument("--prompt", type=str, help="prompt")
    parser2.add_argument("--unprompt", type=str, default="", help="negative prompt")
    parser2.add_argument("--promptparser", type=str, default=None, help="prompt parser")
    # img2img params
    parser2.add_argument("--init-image", type=str, default=None, help="path to initial image")
    parser2.add_argument("--strength", type=float, default=0.5, help="how strong the initial image should be noised [0.0, 1.0]")
    # inpainting
    parser2.add_argument("--mask", type=str, default=None, help="mask of the region to inpaint on the initial image")
    # output name
    parser2.add_argument("--output", type=str, help="output image name, supports {seed} and {step} placeholders")

    while True:
        run_input = input()
        if (run_input.upper() == "EXIT"):
            return

        run_args = parser2.parse_args(shlex.split(run_input))
        run(run_args, engine)


def run(args, engine):
    engine(
        output = args.output.format(seed = args.seed),
        prompt = args.prompt,
        unprompt = args.unprompt,
        promptparser = args.promptparser,
        init_image = None if args.init_image is None else cv2.imread(args.init_image),
        mask = None if args.mask is None else cv2.imread(args.mask, 0),
        strength = args.strength,
        num_inference_steps = args.num_inference_steps,
        guidance_scale = args.guidance_scale,
        eta = args.eta,
        seed = args.seed
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # pipeline configure
    parser.add_argument("--model", type=str, default="bes-dev/stable-diffusion-v1-4-openvino", help="model name")
    parser.add_argument("--model-revision", type=str, default=None, help="model revision")
    # scheduler
    parser.add_argument("--scheduler", type=str, default="LMS", help="scheduler: [LMS, DDIM], will use PNDM for img2img")
    # scheduler params
    parser.add_argument("--beta-start", type=float, default=0.00085, help="LMSDiscreteScheduler::beta_start")
    parser.add_argument("--beta-end", type=float, default=0.012, help="LMSDiscreteScheduler::beta_end")
    parser.add_argument("--beta-schedule", type=str, default="scaled_linear", help="LMSDiscreteScheduler::beta_schedule")
    # tokenizer
    parser.add_argument("--tokenizer", type=str, default="openai/clip-vit-large-patch14", help="tokenizer")
    args = parser.parse_args()
    main(args)
