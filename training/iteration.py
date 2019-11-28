from termcolor import colored


class Iteration(object):
    def __init__(self):
        super(Iteration, self).__init__()

    def common_ops(self):
        self.batch_size = self.data.points.size(0)

        if self.opt.SVR:
            self.data.pointsReconstructed_prims = self.network(self.data.image,
                                                               train=self.flags.train)  # forward pass # batch, nb_prim, num_point, 3
        else:
            self.data.pointsReconstructed_prims = self.network(self.data.points.transpose(2, 1).contiguous(),
                                                               train=self.flags.train)  # forward pass # batch, nb_prim, num_point, 3
        self.fuse_primitives()

        self.loss_model()  # batch
        self.visualize()

    def train_iteration(self):
        self.optimizer.zero_grad()
        self.common_ops()
        self.log.update("loss_train_total", self.data.loss.item())
        if self.opt.learning:
            self.data.loss.backward()
            self.optimizer.step()  # gradient update
        self.print_iteration_stats(self.data.loss)

    def visualize(self):
        if self.iteration % 50 == 1:
            tmp_string = "train" if self.flags.train else "test"
            self.visualizer.show_pointcloud(self.data.points[0], title=f"GT {tmp_string}")
            self.visualizer.show_pointcloud(self.data.pointsReconstructed[0], title=f"Reconstruction {tmp_string}")
            if self.opt.SVR:
                self.visualizer.show_image(self.data.image[0], title=f"Input Image {tmp_string}")

    def test_iteration(self):
        self.common_ops()
        self.num_val_points = self.data.pointsReconstructed.size(1)
        self.log.update("loss_val", self.data.loss.item())
        print(
            '\r' + colored(
                '[%d: %d/%d]' % (self.epoch, self.iteration, self.datasets.len_dataset_test / self.opt.batch_size_test),
                'red') +
            colored('loss_val:  %f' % self.data.loss.item(), 'yellow'),
            end='')
