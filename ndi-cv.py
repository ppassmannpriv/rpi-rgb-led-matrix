import sys;
import time;
import numpy as np;
import cv2 as cv;
import NDIlib as ndi;
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics;
from PIL import Image;
from PIL import ImageDraw;
import socket;

def main():
    options = RGBMatrixOptions();
    options.multiplexing = 0;
    options.row_address_type = 0;
    options.brightness = 100;
    options.rows = 64;
    options.cols = 64;
    options.chain_length = 8;
    options.parallel = 1;
    options.pixel_mapper_config = 'Remap:256,128|0,0s|64,0s|128,0s|192,0s|192,64n|128,64n|64,64n|0,64n';
    options.inverse_colors = False;
    options.led_rgb_sequence = "RGB";
    options.gpio_slowdown = 5;
    options.pwm_lsb_nanoseconds = 50;
    options.show_refresh_rate = 1;
    options.disable_hardware_pulsing = False;
    options.scan_mode = 0;
    options.pwm_bits = 8;
    options.daemon = 0;
    options.drop_privileges = 0;
    display = RGBMatrix(options=options);
    font = graphics.Font();
    font.LoadFont('fonts/6x10.bdf');
    textColor = graphics.Color(255, 0, 0);
    panelname = '256x128_0';

    localIp = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0];

    double_buffer = display.CreateFrameCanvas()
    w = double_buffer.width
    
    if not ndi.initialize():
        return 0;
    
    ndi_find = ndi.find_create_v2();

    if ndi_find is None:
        return 0;

    sources = [];
    while not len(sources) > 0:
        graphics.DrawText(display, font, 5, 10, textColor, "NDI source lookup...");
        graphics.DrawText(display, font, 5, 25, textColor, "IP: " + localIp);
        graphics.DrawText(display, font, 5, 40, textColor, "Display size: 256x128");
        graphics.DrawText(display, font, 5, 55, textColor, "Source name: " + panelname);
        
        ndi.find_wait_for_sources(ndi_find, 1000);
        sources = ndi.find_get_current_sources(ndi_find);

    ndi_recv_create = ndi.RecvCreateV3()
    ndi_recv_create.color_format = ndi.RECV_COLOR_FORMAT_BGRX_BGRA

    ndi_recv = ndi.recv_create_v3(ndi_recv_create)

    if ndi_recv is None:
        return 0

    targetSource = None;
    for source in sources:
        if panelname in source.ndi_name:
            targetSource = source;
    
    if targetSource is None:
        return 0

    ndi.recv_connect(ndi_recv, source)

    ndi.find_destroy(ndi_find)

    cv.startWindowThread()

    while True:
        s = time.time();
        t, v, _, _ = ndi.recv_capture_v2(ndi_recv, 3000)

        if t == ndi.FRAME_TYPE_VIDEO:
            frame = np.copy(v.data);
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB);
            im_pil = Image.fromarray(frame);
            double_buffer.SetImage(im_pil)
            e = time.time()
            double_buffer = display.SwapOnVSync(double_buffer)
            ndi.recv_free_video_v2(ndi_recv, v)

        if cv.waitKey(1) & 0xff == 27:
            break

    ndi.recv_destroy(ndi_recv)
    ndi.destroy()
    cv.destroyAllWindows()

    return 0

if __name__ == "__main__":
    sys.exit(main())
