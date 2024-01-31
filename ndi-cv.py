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
    options.brightness = 90;
    options.rows = 32;
    options.cols = 64;
    options.chain_length = 8;
    options.parallel = 1;
    options.pixel_mapper_config = 'Remap:128,128|0,0s|64,0s|64,32n|0,32n|0,64s|64,64s|64,96n|0,96n';
    options.hardware_mapping = 'adafruit-hat';
    options.inverse_colors = False;
    options.led_rgb_sequence = "RGB";
    options.gpio_slowdown = 4;
    options.pwm_lsb_nanoseconds = 75;
    options.show_refresh_rate = 1;
    options.disable_hardware_pulsing = False;
    options.scan_mode = 0;
    options.pwm_bits = 11;
    options.daemon = 0;
    options.drop_privileges = 0;
    display = RGBMatrix(options=options);
    font = graphics.Font();
    font.LoadFont('fonts/6x10.bdf');
    textColor = graphics.Color(255, 0, 0);

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
        graphics.DrawText(display, font, 0, 10, textColor, "NDI source lookup...");
        graphics.DrawText(display, font, 0, 25, textColor, "IP: " + localIp);
        graphics.DrawText(display, font, 0, 40, textColor, "Display size: 128x128");
        
        ndi.find_wait_for_sources(ndi_find, 1000);
        sources = ndi.find_get_current_sources(ndi_find);

    ndi_recv_create = ndi.RecvCreateV3()
    ndi_recv_create.color_format = ndi.RECV_COLOR_FORMAT_BGRX_BGRA

    ndi_recv = ndi.recv_create_v3(ndi_recv_create)

    if ndi_recv is None:
        return 0

    ndi.recv_connect(ndi_recv, sources[0])

    ndi.find_destroy(ndi_find)

    cv.startWindowThread()

    while True:
        s = time.time();
        t, v, _, _ = ndi.recv_capture_v2(ndi_recv, 5000)

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