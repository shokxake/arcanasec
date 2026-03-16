document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/') {
        const canvas = document.createElement('canvas');
        document.body.prepend(canvas);
        canvas.style.position = 'fixed';
        canvas.style.top = 0;
        canvas.style.left = 0;
        canvas.style.zIndex = -1;

        const ctx = canvas.getContext('2d');

        let canvasWidth = window.innerWidth;
        let canvasHeight = window.innerHeight;
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;

        let numNodes = Math.floor(canvasWidth * canvasHeight / 10000);
        let nodes = [];
        let connectionDistance = Math.min(canvasWidth, canvasHeight) / 6;
        const nodeRadius = 4;
        const nodeColor = 'rgba(255, 255, 255, 0.7)';
        const lineColor = 'rgba(255, 255, 255, 0.3)'; // Chiziqlar rangi oq
        const flowColor = 'rgba(0, 255, 0, 0.8)';
        const flowSpeed = 0.5;

        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        class Node {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = random(-0.5, 0.5);
                this.vy = random(-0.5, 0.5);
                this.alpha = random(0.5, 1);
                this.alphaDirection = random(-0.02, 0.02) > 0 ? 1 : -1;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, nodeRadius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
                ctx.fill();
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > canvasWidth) this.vx *= -1;
                if (this.y < 0 || this.y > canvasHeight) this.vy *= -1;

                this.alpha += this.alphaDirection * 0.01;
                if (this.alpha > 1 || this.alpha < 0.5) this.alphaDirection *= -1;

                this.draw();
            }
        }

        function createNodes() {
            nodes = [];
            for (let i = 0; i < numNodes; i++) {
                nodes.push(new Node(random(0, canvasWidth), random(0, canvasHeight)));
            }
        }

        createNodes();

        function drawConnections() {
            for (let i = 0; i < numNodes; i++) {
                for (let j = i + 1; j < numNodes; j++) {
                    const dx = nodes[i].x - nodes[j].x;
                    const dy = nodes[i].y - nodes[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < connectionDistance) {
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.strokeStyle = lineColor; // Chiziqlar rangi oq
                        ctx.lineWidth = 0.5;
                        ctx.stroke();

                        // Oqim effekti
                        const flowLength = 20;
                        const flowPosition = (Date.now() * flowSpeed) % (2 * distance);
                        const flowStartX = nodes[i].x + (nodes[j].x - nodes[i].x) * (flowPosition / (2 * distance));
                        const flowStartY = nodes[i].y + (nodes[j].y - nodes[i].y) * (flowPosition / (2 * distance));
                        const flowEndX = flowStartX + (nodes[j].x - nodes[i].x) * (flowLength / distance);
                        const flowEndY = flowStartY + (nodes[j].y - nodes[i].y) * (flowLength / distance);

                        ctx.beginPath();
                        ctx.moveTo(flowStartX, flowStartY);
                        ctx.lineTo(flowEndX, flowEndY);
                        ctx.strokeStyle = flowColor;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
        }

        function animate() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);

            for (const node of nodes) {
                node.update();
            }

            drawConnections();

            requestAnimationFrame(animate);
        }

        animate();

        window.addEventListener('resize', function() {
            canvasWidth = window.innerWidth;
            canvasHeight = window.innerHeight;
            canvas.width = canvasWidth;
            canvas.height = canvasHeight;

            numNodes = Math.floor(canvasWidth * canvasHeight / 10000);
            connectionDistance = Math.min(canvasWidth, canvasHeight) / 6;
            createNodes();
        });
    }
});